"""Synthetic leak checks; fixtures do not contain real operator data."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('public_docs', ROOT / 'scripts/check_public_docs.py')
assert SPEC and SPEC.loader
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class PublicDocsTests(unittest.TestCase):
    def test_current_tree(self):
        self.assertEqual(M.check(ROOT), [])

    def test_address(self):
        self.assertIn('IPv4 address', M.sensitive_patterns('.'.join(['192', '0', '2', '10'])))

    def test_mac(self):
        self.assertIn('MAC address', M.sensitive_patterns(':'.join(['00', '11', '22', '33', '44', '55'])))

    def test_ipv6(self):
        self.assertIn('IPv6-like address', M.sensitive_patterns(':'.join(['2001', 'db8', '', '1'])))

    def test_email(self):
        self.assertIn('email address', M.sensitive_patterns('owner' + '@' + 'example.invalid'))

    def test_account_path(self):
        path = 'C:' + '\\' + 'Users' + '\\' + 'example'
        self.assertIn('local account path', M.sensitive_patterns(path))

    def test_mdns_identity(self):
        name = 'adb-' + 'SYNTHETIC-DEVICE' + '._adb-tls-connect._tcp'
        self.assertIn('ADB mDNS identity', M.sensitive_patterns(name))

    def test_pairing_code(self):
        self.assertIn('literal pairing code', M.sensitive_patterns('pairing code: ' + '123' + '456'))

    def test_token_url(self):
        self.assertIn('credential-like URL', M.sensitive_patterns('https://example.invalid/?' + 'token=value'))

    def test_placeholders_are_allowed(self):
        self.assertEqual(M.sensitive_patterns('DEVICE_IP:PAIRING_PORT HEARTH_TARGET'), [])

    def test_firmware_hash_is_allowed(self):
        self.assertEqual(M.sensitive_patterns('a' * 64), [])

    def test_png_reviewed_crop(self):
        self.assertEqual(M.png_errors(ROOT / 'assets/native-navigation.png'), [])

    def test_invalid_png_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'sample.png'
            p.write_bytes(b'not an image')
            self.assertTrue(M.png_errors(p))


if __name__ == '__main__':
    unittest.main()
