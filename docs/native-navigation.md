# Restore the native navigation bar

This procedure uses the navigation code already in Hearth's SystemUI. It does not install a gesture-navigation app.

The tested result was a visible bar with working Back and Home buttons. Recents remained nonfunctional because its configured task switcher was absent. Read [the test conditions](test-record.md) before treating this as a recipe for a different firmware build.

**The test unit already had Nova installed and the `com.hearth.hmf` management package disabled.** On a display with the manager running, it may hide the bar again or turn debugging off. This guide does not disable that package automatically. See [Apps and kiosk behavior](apps-and-kiosk.md) for the consequences of doing so.

## 1. Check the connection and save a baseline

Complete [pairing and target selection](getting-started.md) first. Keep that terminal open so `$Hearth` still selects the correct display.

Run these read-only checks:

```sh
adb -s "$Hearth" get-state
adb -s "$Hearth" shell pm path com.android.systemui
adb -s "$Hearth" shell pm path com.hearth.hmf
adb -s "$Hearth" shell settings get system hide_nav_bar
adb -s "$Hearth" shell settings get secure navigation_mode
adb -s "$Hearth" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
adb -s "$Hearth" shell dumpsys package com.hearth.hmf
```

Save the output privately, outside the repository. The package dump includes user-specific state. In its `User 0` section, `enabled=3` means disabled by the user; `enabled=0` means the manifest's default, not disabled.

On the tested configuration, `hide_nav_bar` began at `1`, navigation mode was `0`, and Home resolved to Nova. If your device has no usable Home app, install and verify one using [Apps and kiosk behavior](apps-and-kiosk.md) before relying on Home as an exit.

You can check for the vendor receiver locally:

```sh
adb -s "$Hearth" shell dumpsys activity broadcasts com.android.systemui
```

Look for `hearth.navbar.show`. Do not post the whole dump publicly. If the action is absent or the package layout differs, stop rather than substituting random system-bar commands.

## 2. Temporarily restart ADB with root access

The existing show-bar broadcast is protected. The normal shell was denied permission to send it. The tested debug build supports:

```sh
adb -s "$Hearth" root
```

This restarts the device's ADB daemon with root privileges where the build permits it. It does not install Magisk, replace recovery, or make a permanent root-framework installation. See AOSP's [root/unroot explanation](https://android.googlesource.com/platform/packages/modules/adb/+/HEAD/docs/dev/root.md).

Expect a brief disconnect. Run `adb mdns services` and `adb devices -l`, or read the current connection port on the display. Reconnect and update `$Hearth` as described in the pairing guide.

Then check:

```sh
adb -s "$Hearth" shell id
```

Proceed only when the intended Hearth returns `uid=0(root)`.

If ADB says it cannot run as root in production builds, stop. This procedure has no verified non-root substitute for the protected broadcast. Do not unlock or reflash the display to force it through.

## 3. Ask SystemUI to show its own bar

Run this one command:

```sh
adb -s "$Hearth" shell am broadcast -a hearth.navbar.show -p com.android.systemui
```

The test returned `Broadcast completed: result=0`, and the bar appeared at the bottom of the display. A successful broadcast response alone is not proof that the UI changed, so check the screen too.

![Restored native navigation strip](../assets/native-navigation.png)

The inspected receiver saves `hide_nav_bar=0` and calls `addNavBar()`. Changing the setting alone did not recreate the missing window during testing. You need the receiver's action, not just the stored flag.

No app or system partition needs to be replaced for this method.

## 4. Check the buttons

```sh
adb -s "$Hearth" shell settings get system hide_nav_bar
adb -s "$Hearth" shell dumpsys window windows
```

The setting should read `0`. In the window output, inspect the `NavigationBar0` section for a surface that is shown and visible. Output layout varies by build; keep that dump private too.

Test the actual buttons on screen:

* Open Android Settings and press **Back**. It should return to the previous app.
* Press **Home**. It should open the selected Home application.
* Press **Recents** separately. Do not count a visible square as a working task switcher.

On the test unit, the configured Recents component was `com.android.launcher3/com.android.quickstep.RecentsActivity`, but `com.android.launcher3` was absent. Its Quickstep service did not resolve. Restoring the bar could not supply that missing code.

A different launcher does not automatically replace the firmware's task-switcher integration. Do not install an arbitrary privileged Launcher3 APK as an assumed fix.

## 5. Return ADB to ordinary shell access

Do this even if an earlier step failed after root access was obtained:

```sh
adb -s "$Hearth" unroot
```

The port can change again. Discover or read the current connection address, reconnect, update `$Hearth`, and verify:

```sh
adb -s "$Hearth" shell id
```

The test returned to `uid=2000(shell)`, while the native bar remained visible. If the connection drops before cleanup, restore ordinary ADB access and verify its identity before considering the session finished. Do not leave an unattended root debugging session running.

Open Hearth again from your launcher when finished. Leave existing gesture software installed until you have tested the native controls you rely on. It is not needed by the show-bar command, but uninstalling it was outside this test.

## What survives?

The receiver writes a stored setting. We verified the bar during the current boot and after returning ADB to shell access. **We have not tested a cold boot, a factory reset, an app update, or a firmware update with this setup.** The management service can issue the hide command again.

Use [Troubleshooting and undo](troubleshooting.md) if the result differs. The [persistence plan](persistence-and-updates.md) explains what still needs testing before owner access and automatic updating can coexist reliably.
