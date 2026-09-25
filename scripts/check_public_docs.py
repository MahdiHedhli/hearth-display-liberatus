"""Offline pre-publication checks. No ADB, network access, or device changes.

This catches common leaks, not all sensitive information. Review prose and pixels.
"""
from __future__ import annotations

import re
import struct
import subprocess
import sys
import zlib
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = frozenset({
    'README.md', 'AGENTS.md', 'CONTRIBUTING.md', '.gitignore',
    '.github/ISSUE_TEMPLATE/compatibility.md',
    'docs/getting-started.md', 'docs/native-navigation.md',
    'docs/apps-and-kiosk.md', 'docs/findings.md', 'docs/test-record.md',
    'docs/troubleshooting.md', 'docs/persistence-and-updates.md',
    'docs/sources.md', 'assets/native-navigation.png',
    'scripts/check_public_docs.py', 'tests/test_public_docs.py',
})
PATTERNS = {
    'IPv4 address': r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])',
    'MAC address': r'(?i)(?<![\w])(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}(?![\w])',
    'IPv6-like address': r'(?i)(?<![\w])(?:[0-9a-f]{0,4}:){3,}[0-9a-f:]{0,39}',
    'email address': r'(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}',
    'local account path': r'(?i)(?:[a-z]:[\\/]Users[\\/]|/(?:Users|home)/)[^\s/\\]+',
    'ADB mDNS identity': r'adb-[A-Za-z0-9_-]{6,}\._adb-tls-',
    'private key': r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    'credential-like URL': r'(?i)[?&](?:token|access_token|auth|key|secret|signature)=[^\s)]+',
    'GitHub token': r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
    'OpenAI-like key': r'sk-[A-Za-z0-9_-]{24,}',
    'literal pairing code': r'(?i)pairing\s+code\s*[:=]\s*\d{6}\b',
}
LINK = re.compile(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)')


def sensitive_patterns(text: str) -> list[str]:
    """Return categories only, never repeat a potential secret in output."""
    return [name for name, pattern in PATTERNS.items() if re.search(pattern, text)]


def candidate_files(root: Path) -> list[str]:
    if (root / '.git').exists():
        proc = subprocess.run(
            ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
            cwd=root, capture_output=True, check=True, timeout=10,
        )
        return sorted(set(proc.stdout.decode('utf-8').strip('\0').split('\0')) - {''})
    return sorted(str(p.relative_to(root)).replace('\\', '/') for p in root.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts and '.git' not in p.parts)


def png_errors(path: Path) -> list[str]:
    data = path.read_bytes()
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        return ['not a PNG']
    pos = 8
    chunks = []
    dimensions = None
    while pos < len(data):
        if pos + 12 > len(data):
            return ['truncated PNG chunk']
        size = struct.unpack('>I', data[pos:pos+4])[0]
        kind = data[pos+4:pos+8]
        end = pos + 12 + size
        if end > len(data):
            return ['truncated PNG data']
        payload = data[pos+8:pos+8+size]
        crc = struct.unpack('>I', data[pos+8+size:end])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            return ['PNG CRC mismatch']
        chunks.append(kind)
        if kind == b'IHDR' and size == 13:
            dimensions = struct.unpack('>II', payload[:8])
        pos = end
    errors = []
    if any(c not in (b'IHDR', b'IDAT', b'IEND') for c in chunks):
        errors.append('PNG contains metadata or unexpected chunks')
    if dimensions != (1080, 56):
        errors.append('image dimensions differ from the reviewed navigation-only crop')
    if not chunks or chunks[0] != b'IHDR' or chunks[-1] != b'IEND':
        errors.append('invalid PNG chunk order')
    return errors


def check(root: Path) -> list[str]:
    problems = []
    paths = candidate_files(root)
    for relative in paths:
        if relative not in PUBLIC_FILES:
            problems.append(f'{relative}: unexpected public file; explicit review required')
            continue
        path = root / relative
        if path.is_symlink():
            problems.append(f'{relative}: symlinks are not allowed')
            continue
        if path.suffix == '.png':
            problems.extend(f'{relative}: {e}' for e in png_errors(path))
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeError:
            problems.append(f'{relative}: not UTF-8 text')
            continue
        problems.extend(f'{relative}: potential {p}' for p in sensitive_patterns(text))
        if path.suffix != '.md':
            continue
        if '\u2014' in text or '\u2013' in text:
            problems.append(f'{relative}: rewrite prose dashes')
        if text.count('```') % 2:
            problems.append(f'{relative}: unclosed code fence')
        for target in LINK.findall(text):
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            linked = (path.parent / unquote(parts.path)).resolve()
            if not linked.is_relative_to(root.resolve()) or not linked.is_file():
                problems.append(f'{relative}: broken or escaping relative file link')
        in_code = False
        for line in text.splitlines():
            if line.startswith('```'):
                in_code = not in_code
            elif in_code and line.startswith('adb '):
                command = line[4:]
                allowed = ('-s "$Hearth" ', 'pair ', 'connect ', 'devices ', 'mdns ', 'version')
                if not command.startswith(allowed):
                    problems.append(f'{relative}: unscoped or unexpected ADB command')
    for required in PUBLIC_FILES:
        if required not in paths:
            problems.append(f'{required}: expected reviewed file missing')
    return problems


def main() -> int:
    try:
        problems = check(ROOT)
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f'CHECK FAILED: {type(exc).__name__}', file=sys.stderr)
        return 2
    if problems:
        print('\n'.join(problems))
        return 1
    print(f'PASS: {len(PUBLIC_FILES)} reviewed file paths; privacy patterns, links, PNG, and ADB scope.')
    print('This is an offline documentation check, not a hardware test or complete privacy guarantee.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
