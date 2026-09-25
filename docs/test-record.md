# Anonymized test record

Recorded in September 2026. This is a summary of operator-held evidence, not a public release of raw device logs or a reproducible automated device test suite.

## Scope

One already-modified Hearth Display running Android 11 was inspected. Its software reported product/device `rk3566_r`, model `rk3568`, a January 2026 `userdebug` build, and `ro.debuggable=1`. Those are firmware identifiers, not independent physical-chip identification.

The installed management APK reported package `com.hearth.hmf`, versionName `11`, versionCode `30`. The Hearth interface reported `com.nativeapp`, versionName `2.67.0`. A future reader should compare their own installed versions rather than assume these are current releases.

The management APK inspected had SHA-256:

```text
24f948bf98a79502352523c3eed5a1754f0ada4b8ee16468a171eb834aa768c3
```

This identifies the copied software artifact, not a household, device serial, or account. The APK and decompiled source are not distributed here. JADX reported five errors across the decompilation; only the readable methods and manifest actually inspected support the code findings.

## Conditions before the navigation test

`com.hearth.hmf` was disabled for user 0. `com.nativeapp` was enabled. Nova was the selected Home application. Existing gesture and launcher accessibility services were still present. Android lock-task mode reported `NONE`.

The navigation setting `hide_nav_bar` was `1`; three-button mode was reported, but the navigation window was missing. These conditions matter: this was not a clean-room test with every third-party component removed, and full kiosk behavior was not running.

## Results

| Check | Result | Limit |
| --- | --- | --- |
| Authorized ADB connection | Passed | Does not document a pairing bypass |
| Temporary `adb root` | UID 0 verified after reconnect | Only this debug build |
| Show broadcast from UID 2000 | Permission denied | Expected protected-broadcast boundary |
| Show broadcast from root | Bar appeared | With management package disabled |
| Native Back button | Returned from Settings to Hearth | Observed through on-screen tap |
| Native Home button | Opened Nova | Selected Home was already installed |
| Native Recents button | Did not open overview | Configured Quickstep provider absent |
| `adb unroot` | UID 2000 verified after reconnect | Not a device reboot |
| Navigation after unroot | Still visible; setting read `0` | Current boot only |
| Normal Hearth interface | Left in foreground | Not full feature qualification |
| Sleep schedule | Settings present; service unavailable to checks | No repaired sleep/wake test |
| Updates | Code inspected | No app or firmware update performed |

## What has not been tested

Cold boot with the restored bar; removal of existing gesture software; live scheduler restoration; update-preserving service isolation; a real app-update or firmware-update cycle; restoration from a firmware backup; a repaired task switcher; and Google Play installation all remain unverified.

No system APK was replaced, no recovery image was flashed, and no bootloader operation or factory reset was performed during the navigation restoration.

## How to add another result

Report the non-unique Android version, build type, HMF version, package enabled state, selected launcher name, and the command/result being tested. State separately whether a reboot or update was performed.

Leave out full fingerprints with build-user details, serials, host paths, addresses, pairing information, family content, and raw logs. Use the [compatibility report template](../.github/ISSUE_TEMPLATE/compatibility.md).
