# Hearth Display Liberatus

Get Android's own Back and Home buttons working on a Hearth Display, keep access to the apps you install, and understand which Hearth features depend on its kiosk software.

The display we tested already had a navigation bar. Hearth's customized SystemUI had removed it. An existing vendor broadcast brought it back without installing a gesture app, replacing SystemUI, or flashing firmware.

![Native Android navigation bar restored on the tested display](assets/native-navigation.png)

**Back and Home worked in live tests. The Recents button appeared, but its task-switcher component was missing. Reboot and firmware-update survival have not been tested.** See the [test record](docs/test-record.md) for the conditions behind those results.

## Start here

[Enable developer options and pair ADB](docs/getting-started.md), then [restore the native navigation bar](docs/native-navigation.md).

Already paired? Start with the navigation guide. It explains the temporary root step, the changing wireless port, verification, and how to return ADB to ordinary shell access. No third-party navigation app is required by the procedure. Existing gesture software was present during testing; its removal has not been tested.

For running other apps, read [Apps and kiosk behavior](docs/apps-and-kiosk.md) before disabling anything. The management package also contains Hearth's sleep scheduler and update handling. Disabling that entire package has costs.

## What this repository covers

| Topic | Current evidence |
| --- | --- |
| Developer options and wireless pairing | Documented by the original community guide and Android; authorized ADB access verified on the test unit |
| Built-in ADB root | Worked on the tested Android 11 `userdebug` build |
| Native navigation | Bar restored; Back and Home taps worked |
| Recents | Visible button, missing Launcher3/Quickstep implementation |
| Kiosk controls | Management behavior inspected; alternate Home and Hearth app coexist in the tested configuration |
| Scheduled sleep | Saved schedule found; required service unavailable in the tested disabled-package state |
| Updates without lockout | Research plan only |
| Google Play | Not installed or tested |

These results come from one already-modified display. They are not a compatibility claim for every Hearth model or a fresh-device installation test. The [findings register](docs/findings.md) distinguishes live results, inspected code, and open questions.

## Before changing a family appliance

Use a device you own or have permission to administer. Work while nobody depends on the display. Keep physical access and a private record of the settings you change.

Root commands can change far more than a navigation bar. Stop if the build, package names, permissions, or results differ from the guide. There is no firmware flash, factory reset, bootloader operation, or permanent root installation in these instructions. Do not expose ADB to the internet.

For recovery details, use [Troubleshooting and undo](docs/troubleshooting.md). For longer-term work, see [Persistence, updates, and Google Play](docs/persistence-and-updates.md). That page is a plan, not an update-proof hack.

## Credit and sources

[mbazos/hearth-hacking](https://github.com/mbazos/hearth-hacking) documented the developer-options route, wireless ADB access, and kiosk-package workaround that provided the starting point. This guide rewrites those steps and adds the native navigation method and its limitations. It does not copy the other repository's APK archive.

[Sources and attribution](docs/sources.md) identifies the upstream revision and Android documentation. This is an independent owner project, with no affiliation with Hearth, Rockchip, or Google.

## Share results without sharing your household

Read [CONTRIBUTING.md](CONTRIBUTING.md) before posting logs or screenshots. Keep serials, pairing codes, network details, account data, and family content out of issues and commits. Raw device dumps and vendor APKs do not belong here.
