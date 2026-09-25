# Troubleshooting and undo

Keep physical access to the display. Before another change, confirm which device `$Hearth` selects and whether the shell is root. The [navigation procedure](native-navigation.md) explains both checks.

## The connection vanished after root or unroot

The daemon restarts, and the wireless port can change. Read the main Wireless debugging screen, or use `adb mdns services` and `adb devices -l`. Connect to the current `_adb-tls-connect._tcp` address and update `$Hearth`.

A stale offline entry does not mean the device needs to be paired again. First try the current connection address with the existing authorization. Pair again only when authorization is actually needed, using a new on-screen code.

Do not run `adb kill-server` as the first response. It disconnects the computer's other ADB sessions too. Do not guess a static port or open the service to the internet.

## Permission denied when sending the show command

Check:

```sh
adb -s "$Hearth" shell id
```

The tested show action required UID 0. Follow the temporary-root step, rediscover the connection, and verify root on the correct device. If the build rejects root or still rejects the broadcast, stop and record the difference. Do not weaken SELinux or replace system packages to make this guide apply.

## The setting is zero but there is no bar

The inspected receiver does two things: it saves `hide_nav_bar=0` and calls the navigation controller. Merely writing the setting did not recreate the window in testing. Use the targeted show broadcast and inspect the screen, not just the setting.

If the action is missing from your build, or the manager hides the bar again, the tested conditions do not apply. Inspect package state before deciding whether to accept the tradeoffs in [Apps and kiosk behavior](apps-and-kiosk.md).

## Home does not give me a usable launcher

Check the selected Home component:

```sh
adb -s "$Hearth" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
```

Install and finish setting up a compatible Home app before choosing it. Record the old component. Do not select Settings' `FallbackHome` as a general-purpose launcher; it is not an app drawer.

## The Recents square does nothing

The test unit lacked its configured Launcher3/Quickstep provider. A visible button is not the implementation behind that button. This repository has no tested repair. Back and Home can still work independently.

## Scheduled sleep stopped after disabling the manager

Do not immediately add another timer. The management package contains Hearth's own scheduler. The saved schedule can remain enabled even when the service that executes it is unavailable.

The [findings register](findings.md) explains the service boundary. Restoring only the power service is still proposed work. Re-enabling all of HMF may also restart kiosk enforcement, debugging restrictions, and update activity.

## Undo only the navigation change

The counterpart `hearth.navbar.hide` receiver was found in the inspected SystemUI code. It stores `hide_nav_bar=1` and removes the bar. **This undo action is code-inspected, not a separately completed live rollback test.** Use it only when restoring your recorded pre-change hidden state and after confirming another way to navigate.

With temporary root already verified on the current target:

```sh
adb -s "$Hearth" shell am broadcast -a hearth.navbar.hide -p com.android.systemui
adb -s "$Hearth" unroot
```

Rediscover the connection and verify `uid=2000(shell)`. Hiding the bar does not restore disabled packages, the previous Home app, or firmware state.

## Undo a Home or package change

Restore the component and package states you recorded, not a guessed stock configuration.

For a known previous Home component:

```sh
adb -s "$Hearth" shell cmd package set-home-activity PREVIOUS_HOME_COMPONENT
```

Package Manager distinguishes an explicit enabled override from the manifest's default. To remove your override for a package that originally used the default state, `pm default-state --user 0 PACKAGE_NAME` is the relevant operation. To restore an explicitly enabled state, use `pm enable --user 0 PACKAGE_NAME`. Verify the command in your build's `pm help` before use. These state-restoration instructions have not been exercised as a full rollback on this unit.

**Restoring `com.hearth.hmf` can cost you the ADB connection.** Its startup policy can disable developer options and both debugging modes. Restore it only beside the display, with a recovery plan, and expect normal kiosk/update activity to resume. Do not combine enable, reboot, and cleanup into an unattended script.

## After maintenance

Return ADB to shell access, check the selected Home and Hearth UI, and close any temporary transfer service you opened. Turn wireless debugging off or forget unused paired computers when remote maintenance is no longer needed. Keep your ADB private key protected.

Do not publish a screenshot of a pairing dialog, a whole bug report, or a family calendar while asking for help. [CONTRIBUTING.md](../CONTRIBUTING.md) explains what to share instead.
