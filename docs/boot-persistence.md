# Keep navigation and Hearth visible after reboot

This page documents a reboot-persistence fix tested on one already-modified Android 11 userdebug Hearth Display. It does not require Termux, Tailscale, a replacement launcher, or a new system APK.

Use this only after the one-boot navigation procedure works on your display. Keep physical access and an authorized ADB connection available until the reboot test passes.

## Why the bar disappeared again

The tested firmware already contains a root boot service in /system/etc/init/myrc.rc:

~~~text
service runapp /system/bin/startonboot.sh
        class main
        seclabel u:r:su:s0
        user root
        group root
        oneshot
        disabled

on property:dev.bootcomplete=1
       start runapp
~~~

Its /system/bin/startonboot.sh handles normal Hearth startup tasks. In the post-onboarding path, the inspected script explicitly sends hearth.navbar.hide. The line that would start the normal Hearth application is commented out.

That explains two symptoms seen after leaving the original kiosk behavior:

* a reboot can hide Android's native navigation bar again;
* if another launcher is selected as Home, the display can remain on that launcher instead of returning to Hearth.
The fix below extends the existing firmware boot hook. It does not replace init or install a permanent root framework.

## 1. Confirm this firmware has the expected hook

Pair ADB and select the intended display as $Hearth using [Getting started](getting-started.md). Then inspect the files before changing them:

~~~sh
adb -s "$Hearth" root
~~~

Reconnect after the ADB daemon restarts, then verify UID 0 and run:

~~~sh
adb -s "$Hearth" shell id
adb -s "$Hearth" shell cat /system/etc/init/myrc.rc
adb -s "$Hearth" shell sed -n '1,220p' /system/bin/startonboot.sh
~~~

Stop if myrc.rc does not start /system/bin/startonboot.sh on dev.bootcomplete=1, or if the startup script is materially different. Do not copy this patch onto an unknown firmware revision.

## 2. Make /system writable through the debug build's overlay

On the tested userdebug build:

~~~sh
adb -s "$Hearth" remount
~~~

The test unit reported that OverlayFS was being used for /system. This is still a system-file modification. It may affect future OTA behavior and is not claimed to be update-safe.
Create a rollback copy before editing:

~~~sh
adb -s "$Hearth" shell 'test -e /system/bin/startonboot.sh.owner-backup || cp -p /system/bin/startonboot.sh /system/bin/startonboot.sh.owner-backup'
~~~

Keep another private off-device copy too.

## 3. Append an owner-persistence block

Append the following block to the end of /system/bin/startonboot.sh:

~~~sh
# === HEARTH OWNER PERSISTENCE BEGIN ===
# Run only after the display has completed normal Hearth onboarding.
if [ -e /data/vendor/hearth/onboardingComplete.txt ]; then
    # The vendor boot script hides this bar earlier. Restore it after that step.
    su -0 am broadcast -a hearth.navbar.show
    su -0 settings put system hide_nav_bar 0

    # An alternate Home launcher can finish initializing after the early boot
    # script. Wait briefly, then bring the normal Hearth UI to the foreground.
    sleep 12
    su -0 am start --user 0 -n com.nativeapp/.MainActivity
fi
# === HEARTH OWNER PERSISTENCE END ===
~~~

Why both navigation commands? On the tested unit, hide_nav_bar=0 alone did not recreate a missing navigation window. The hearth.navbar.show receiver both saves the setting and asks SystemUI to add the bar.

Why the delay? An immediate Hearth launch could be overtaken later by the selected Home launcher while Android finished booting. A delayed second launch was the reliable behavior observed during reboot testing.

The public block above is intentionally limited to navigation and the Hearth interface. It contains no remote-access service.
After editing, validate the shell syntax and restore expected ownership, mode, and SELinux label:

~~~sh
adb -s "$Hearth" shell sh -n /system/bin/startonboot.sh
adb -s "$Hearth" shell chown root:shell /system/bin/startonboot.sh
adb -s "$Hearth" shell chmod 0755 /system/bin/startonboot.sh
adb -s "$Hearth" shell chcon u:object_r:system_file:s0 /system/bin/startonboot.sh
~~~

Then return ADB to ordinary shell mode:

~~~sh
adb -s "$Hearth" unroot
~~~

Rediscover the wireless connection if its port changes.

## 4. Reboot and verify the display, not just the commands

Reboot only when you are beside the display and have a recovery path.

After boot, verify on screen that the native navigation bar is visible, Hearth is in the foreground, and Back and Home still work as expected.

When ADB is available, verify:

~~~sh
adb -s "$Hearth" shell settings get system hide_nav_bar
adb -s "$Hearth" shell dumpsys activity activities
~~~

The tested persistent configuration restored hide_nav_bar to 0 after reboot. The early boot phase briefly showed the alternate launcher, so final foreground must be checked after the delayed Hearth launch rather than immediately when Android first becomes responsive.

## Roll back this boot customization

With temporary root and writable OverlayFS available, restore the saved script:

~~~sh
adb -s "$Hearth" root
~~~

Reconnect and verify UID 0, then:

~~~sh
adb -s "$Hearth" shell cp -p /system/bin/startonboot.sh.owner-backup /system/bin/startonboot.sh
adb -s "$Hearth" shell chown root:shell /system/bin/startonboot.sh
adb -s "$Hearth" shell chmod 0755 /system/bin/startonboot.sh
adb -s "$Hearth" shell chcon u:object_r:system_file:s0 /system/bin/startonboot.sh
adb -s "$Hearth" unroot
~~~

Reboot and verify the original behavior you recorded. The stock tested script hides the navigation bar after onboarding, so restoring it can intentionally bring that behavior back.

## What this does not solve

This patch does not repair Recents, restore Hearth's disabled management or sleep services, preserve wireless debugging, or prove firmware-update compatibility. It also does not make arbitrary future firmware revisions safe to patch.

A vendor update can replace the init file or startup script, change the protected navigation actions, or reject OverlayFS changes. Reinspect the installed firmware after an update instead of automatically reapplying an old patch.
