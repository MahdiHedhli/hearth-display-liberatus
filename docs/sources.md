# Sources and attribution

## Community starting point

[mbazos/hearth-hacking](https://github.com/mbazos/hearth-hacking), reviewed at commit `b540ba0223169b3adaf426bc2695e67823e24b02`:

* [README](https://github.com/mbazos/hearth-hacking/blob/b540ba0223169b3adaf426bc2695e67823e24b02/README.md): developer-options menus and paired wireless debugging.
* [HEARTH_HACKING.md](https://github.com/mbazos/hearth-hacking/blob/b540ba0223169b3adaf426bc2695e67823e24b02/HEARTH_HACKING.md): package-disable workaround, alternate Home, and the upstream full-kiosk restore procedure.
* [Video linked by that README](https://youtube.com/shorts/VGBEjFyY7hs): supplemental menu walkthrough. The video itself was not used as independent verification of the current firmware's menus.

This repository gives original instructions based on those documented steps and the tests described here. It does not reproduce the upstream guide wholesale, redistribute its app archive, or claim authorship of its initial access discovery. An attribution link is not permission to redistribute another project's code or binaries.

## Tests and installed-software inspection

The [anonymized test record](test-record.md) describes the one-unit scope. The original HMF and SystemUI APKs were copied from an owner-authorized display and inspected locally. Readable methods, manifest entries, selected runtime output, and on-screen button tests support the [findings register](findings.md).

The test record is the public summary. Raw logs, full screenshots, APKs, decompiled vendor source, pairing records, and household configuration remain private. This limits independent reproduction from the repository alone; another owner can check the documented methods against their own software and report a sanitized result.

## Android and vendor references

* [SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools): obtain ADB from Google.
* [Developer options](https://developer.android.com/studio/debug/dev-options): reveal the developer-options menu.
* [ADB documentation](https://developer.android.com/tools/adb): pairing, selecting a target, installing APKs, and shell commands. Current documentation also covers newer Android versions; do not assume newer behavior applies to Android 11.
* [ADB root/unroot internals](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/root.md): daemon privilege changes on supported builds.
* [Hearth Sleep Mode](https://hearth.zendesk.com/hc/en-us/articles/35235870141715-Sleep-Mode): intended scheduling and wake behavior, not evidence that the modified configuration passes those tests.
* [Verified Boot](https://source.android.com/docs/security/features/verifiedboot) and [OTA signing](https://source.android.com/docs/core/ota/sign_builds): recovery and update constraints.
* [Block-based OTA](https://source.android.com/docs/core/ota/nonab/block): implications of system modifications for those updates.
* [Google Mobile Services](https://www.android.com/gms/) and [Play Protect certification](https://support.google.com/googleplay/answer/7165974?hl=en): Google Play limitations.

## Writing

The prose was edited using the [Humanizer skill](https://github.com/blader/humanizer/blob/main/SKILL.md), version 3.0.0. It is an editing aid, not a technical source. Claims and commands remain tied to the references and test record above.
