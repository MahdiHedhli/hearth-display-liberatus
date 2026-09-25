# Apps and kiosk behavior

Back and Home make the display easier to use, but they do not change Hearth's foreground policy. Its management service may bring the Hearth app back when you open another application. This is separate from whether the navigation bar is visible.

The configuration used for the native-bar test had `com.hearth.hmf` disabled, `com.nativeapp` enabled, and Nova selected as Home. The Hearth app could run in the foreground, and the native Home button opened Nova. Scheduled sleep and normal update delivery were not restored in that configuration.

## Install and check a Home app

An Android launcher supplies the Home screen and app drawer. It is separate from a gesture-navigation overlay. Nova 8.3.5 was already installed on the test unit; it is an example here, not a bundled dependency or a claim about the best current launcher.

Obtain your chosen launcher from its publisher or another source whose signing identity you can verify. Use an APK compatible with your measured Android version and ABI. Keep APKs outside this repository.

With the target variable from [Getting started](getting-started.md):

```sh
adb -s "$Hearth" shell getprop ro.product.cpu.abilist
adb -s "$Hearth" install 'PATH_TO_LAUNCHER.apk'
```

If it is already installed, do not uninstall it merely to follow this example. Inspect its existing state first. Launch it, finish any setup, and confirm it works before changing the default Home.

For an installed Nova package, resolve its Home component:

```sh
adb -s "$Hearth" shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME -p com.teslacoilsw.launcher
```

On the tested installation, that component was `com.teslacoilsw.launcher/.NovaLauncher`. Record the old default before using the following optional change:

```sh
adb -s "$Hearth" shell cmd package set-home-activity com.teslacoilsw.launcher/.NovaLauncher
```

Use the component actually returned for your launcher. A missing or different result is a reason to stop and inspect, not guess the class name.

## The package-disable workaround has side effects

The [original community guide](https://github.com/mbazos/hearth-hacking/blob/b540ba0223169b3adaf426bc2695e67823e24b02/HEARTH_HACKING.md) describes disabling both Hearth packages. It reports persistence across reboot. This project did not repeat that whole fresh-device procedure or independently qualify its reboot behavior.

For readers who deliberately choose the package-disable workaround, the management-package command is:

```sh
adb -s "$Hearth" shell pm disable-user --user 0 com.hearth.hmf
```

Run it only after saving the original package state and establishing a working alternate Home and access route. The upstream procedure uses root; use the temporary-root and reconnect steps in the [navigation guide](native-navigation.md) when required, and finish with `adb unroot`.

**Disabling this package takes its power/scheduler and update services out of normal service operation too.** On the inspected unit, saved sleep settings remained, but no active management services were reported and the shell could not find `hearth_ipc`. Keeping the main Hearth app open was not enough to restore scheduled sleep.

To keep the Hearth interface usable, this project does not prescribe disabling `com.nativeapp`. If you previously disabled it, inspect that package state and deliberately re-enable it when returning to the Hearth UI:

```sh
adb -s "$Hearth" shell pm enable --user 0 com.nativeapp
```

Launch Hearth through its normal launcher entry. The interface loading is only a UI check; verify calendar sync, routines, sleep, and updates separately. This package combination is not a completed "stock features plus permanent owner access" solution.

## Keep or remove existing gesture software?

The native bar is drawn by SystemUI. No new accessibility service is required for the show-bar method. Existing gesture software was left in place during testing.

After testing the native buttons, you can turn off an unwanted gesture service through Android **Settings**, **Accessibility**, then that service's own switch. Check that this does not remove your only working way to navigate. Removal and interference testing remain unverified here.

Do not overwrite the entire `enabled_accessibility_services` setting to remove one app. That can disable other services you use.

## Returning to stock behavior

Re-enabling `com.hearth.hmf` may restart policies that hide navigation, reclaim the foreground, and disable debugging. It may also resume update work. The original guide's full restore sequence is linked above for attribution; we do not present it as a verified, access-preserving rollback.

Read [Troubleshooting and undo](troubleshooting.md) before restoring package state. Work beside the display, preserve your alternate access tools, and expect that the ADB connection may disappear.
