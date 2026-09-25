# Findings register

These entries describe one owner-operated test configuration and readable portions of its installed software. They are not CVEs, an internet-accessible exploit chain, or a claim that every Hearth has the same behavior.

**Tested** means a live action and its result were observed. **Inspected** means readable code or configuration supports the finding. **Proposed** means implementation or validation remains unfinished. The [test record](test-record.md) provides the scope and limitations.

## LIB-001: built-in debug root

Status: Tested. Requires an already-authorized ADB connection and a firmware build that permits `adb root`.

The tested Android 11 `userdebug` build restarted adbd as root. After reconnecting, `shell id` returned UID 0. `adb unroot` returned it to UID 2000. Wireless connection ports changed during daemon restarts.

This uses the firmware's existing debugging capability. It does not bypass pairing, compromise another user's account, or establish permanent root. AOSP documents the [root/unroot mechanism](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/root.md).

## LIB-002: native navigation can be restored

Status: Tested, with code inspection explaining the result.

In `com.android.systemui.statusbar.phone.StatusBar`, the receiver for `hearth.navbar.show` stores `Settings.System.hide_nav_bar=0` and calls `addNavBar()`. That method asks the navigation controller to create the missing bar for the display. The corresponding `hearth.navbar.hide` action stores `1` and removes it.

Sending the show action from the ordinary shell produced a permission denial. Sending it after obtaining built-in debug root restored the bar. Back and Home responded to actual button taps. The setting alone had not recreated the bar.

The inspected HMF manifest declares these actions as protected broadcasts. The fact that the receiver exists does not make it an unauthenticated remote-control interface. The [navigation guide](native-navigation.md) contains the tested command and cleanup.

## LIB-003: missing Recents implementation

Status: Tested limitation plus inspected runtime configuration.

SystemUI's Recents configuration pointed to `com.android.launcher3/com.android.quickstep.RecentsActivity`. The Launcher3 package was absent, its `android.intent.action.QUICKSTEP_SERVICE` did not resolve, and the overview service reported no connection. The visible Recents button did not open a task switcher.

This explains that unit's result. It does not prove Recents is missing from every revision, and adding a random launcher is not a verified repair.

## LIB-004: debugging policy shares the update cohort

Status: Inspected. The cause of a particular past disconnection was not established.

`AdbSecurityMonitor.checkAdb()` reads the secure setting `memfault_cohort`. A null or `default` value leads `setDebuggingFeatures()` to write zero to the global settings for developer options, USB debugging, and Wi-Fi debugging. The class registers an observer for changes to the cohort setting.

`HMFService.onCreate()` constructs that monitor. Its heartbeat also obtains the assigned cohort from the backend and stores it locally; the update code uses cohort information too.

Changing the cohort locally is therefore not an update-safe persistence technique. It can be overwritten and may affect release selection. No backend credentials, private API requests, device IDs, or cohort-spoofing procedure are published here.

## LIB-005: disabling HMF also removes scheduled-sleep support

Status: Runtime observations and inspected code; the proposed repair is untested.

The manifest declares both `HMFService` and `PrivilegedService`. `SystemBroadcastReceiver` attempts to start both at boot.

`PrivilegedService` implements the display scheduler and registers `hearth_ipc`. It reads the global settings `hearth_display_scheduler_active`, `hearth_display_scheduler_start`, and `hearth_display_scheduler_stop`.

In the tested disabled-package state, the schedule was still enabled in stored settings, no management services were reported active, and `service check hearth_ipc` returned not found from the shell. A persistent process with the package name still existed. A PID alone was therefore not evidence of a working scheduler.

`HMFService.restoreAndroidSettings()` also sets the ordinary screen timeout to `Integer.MAX_VALUE`, about 25 days. The stored value matched that code. It should not be mistaken for an accidental user-selected timeout.

Restoring only the required power service is a research direction. It needs a dependency audit and a real sleep/wake test before it can be called a fix. Hearth documents its intended scheduled-sleep behavior in [Sleep Mode](https://hearth.zendesk.com/hc/en-us/articles/35235870141715-Sleep-Mode).

## LIB-006: update delivery and foreground enforcement are coupled

Status: Inspected.

`HMFService` monitors foreground applications, can restart the main Hearth app, constructs the debugging-policy monitor, and runs application-update and firmware-update tasks. Disabling it to avoid kiosk behavior also removes those normal update checks.

App updates and firmware updates take separate paths in the inspected code. Seeing new calendar data or web-delivered content does not prove either update path is working. A future owner-controlled update tool would need to preserve genuine release selection, signing identity, and verification.

## Research that is not a usable exploit yet

There is no released owner-helper app, update-proof persistence mechanism, repaired Quickstep integration, or working Google Play deployment in this repository. No current method is claimed to survive an arbitrary future firmware change.

The [research plan](persistence-and-updates.md) lists the next bounded experiments. Do not turn its proposals into copy-and-paste repair instructions without evidence.
