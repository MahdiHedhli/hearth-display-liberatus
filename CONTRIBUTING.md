# Contributing

Useful reports say what you tried, what changed, and what did not work. A failed check on another firmware version is worth recording.

Read the [test record](docs/test-record.md) before calling something tested. Label results as **tested**, **inspected**, **reported by upstream**, or **proposed**. A command returning success does not prove the button, scheduler, or update works. Record what you checked on the actual display.

## Privacy review before publishing

Do not upload raw logs, bug reports, UI dumps, pairing screens, account databases, vendor APKs, firmware images, or decompiled proprietary source. Keep private captures outside the checkout. `.gitignore` is a convenience, not a protection against `git add -f` or already-tracked files.

Remove all of the following from text, images, filenames, branches, and commit messages:

* IP and MAC addresses, SSIDs, local hostnames, network topology, serials, and mDNS device names.
* Pairing codes, ADB keys, API keys, session cookies, download tokens, and calendar-subscription links.
* User-account paths, real household names, emails, schedules, routine details, photos, and camera content.

Use `DEVICE_IP`, `PAIRING_PORT`, `CONNECTION_PORT`, and `HEARTH_TARGET` in examples. Do not replace real addresses with slightly changed addresses that still reveal the network layout.

For screenshots, physically crop to the needed UI before sharing and re-encode the image without metadata. Inspect the pixels. A full-screen image concealed by a Markdown crop is still a full-screen image.

Check the staged diff and all new assets before a commit. Review commit author/committer identity too; use a suitable GitHub no-reply address rather than exposing a personal email unintentionally. The repository owner's public GitHub identity and explicit upstream credits are expected public information.

## Local checks

From the repository root, with Python 3 available:

```sh
python3 scripts/check_public_docs.py
python3 -m unittest discover -s tests -v
```

On Windows, use `python` if that is your Python command.

These checks look for common sensitive patterns, unexpected tracked files, broken relative file links, and documentation mistakes. They never connect to a device or run ADB. They cannot determine whether every screenshot or sentence is private; human review is still required.

## Changes worth accepting

Keep the beginner guides readable. Explain a risky command before showing it, include expected results, and provide cleanup. Keep experimental persistence work out of the tested navigation recipe.

Submit only material you have the right to publish. Vendor trademarks and software remain their owners' property. No vendor APK or firmware license is supplied by this repository.
