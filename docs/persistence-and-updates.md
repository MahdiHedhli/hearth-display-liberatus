# Persistence, updates, and Google Play

Status: research plan. None of the helper, service-isolation, or update tooling described here has been deployed or qualified by this project.

The goal is a Hearth that runs its normal family interface and sleep schedule while the owner can open other apps and maintain the device. The current package-disable workaround does not meet that goal: it avoids the foreground watchdog at the cost of other management functions.

## Start with a recovery path

Before a firmware experiment, preserve the exact installed software, configuration, and whatever data can be backed up coherently. Store that material privately off the display. An APK copy is not a ROM backup.

Identify the actual partition layout, accepted update format, and physical recovery route. A public dump with a matching chip-family name is not proof that it can restore this board. An apparently unlocked bootloader is not proof that a downgrade will work. Android documents [Verified Boot](https://source.android.com/docs/security/features/verifiedboot) and [OTA signing](https://source.android.com/docs/core/ota/sign_builds) separately for good reason.

Do not replace recovery, relock the bootloader, or modify read-only system partitions as part of a navigation fix.

## Restore only the services needed for normal use

The next proposed experiment is to audit every startup route, then see whether `PrivilegedService` can run without `HMFService`. Component overrides would need to be prepared while the package is still disabled, before any package enable operation can start the restrictive manager.

This needs a caller-permission review and tests for scheduled sleep, touch wake, app switching, and reboot. It also needs a reliable boot path. An exported service is not proof that an ordinary background app can start it whenever needed.

Even if this split works, it will not restore update handling. That code lives in `HMFService`.

## Keep an independent owner-access route

A small owner-controls helper might provide a visible maintenance screen, a return-to-Hearth action, and narrowly authorized settings recovery. It should not contain a language model, scrape family data, or expose a general remote shell.

Its permissions must be demonstrated, not assumed. In particular, an ordinary installed app cannot be presumed to administer other packages or send a protected vendor broadcast. A useful recovery test would deliberately turn off debugging while another safety route is available, then prove recovery without using the lost ADB connection.

A trusted computer can monitor release versions and access health, but the display's normal operation must not depend on that computer being awake. Avoid a process that repeatedly fights the vendor for the foreground.

## Separate update discovery from installation

Application updates and full firmware updates have different risks. A proposed owner-mediated updater would stage only the genuine signed release offered for that device, validate package/signing identity and compatibility, and require approval before installation.

Changing `memfault_cohort`, the device serial, board identity, or build fingerprint is not part of that plan. The inspected code obtains cohort assignment from the backend, and it affects updates as well as debugging policy.

Keep original vendor signatures and normal verification intact. System-file modifications can also complicate [incremental OTA updates](https://source.android.com/docs/core/ota/nonab/block). A previous APK alone does not guarantee rollback after an application changes its database.

The acceptance test must include a real compatible update, followed by checks of navigation, independent app use, the original sleep schedule, and owner access. Until then, "OTA-safe" is an unearned label. Unknown firmware should prompt inspection rather than automatic reapplication of old commands.

No ordinary app can guarantee continued authority over every future vendor-controlled operating system. A permanent owner-controlled firmware would be a separate project with different update and recovery obligations.

## Google Play is a separate experiment

The inspected package inventory did not contain Play Store, Google Play services, or Google Services Framework. There is no hidden Store switch established by this work.

Sideloading an ordinary APK already works on the tested configuration. Adding a functional Google stack has not been tested. Google Mobile Services is [separate from AOSP](https://www.android.com/gms/), and [Play Protect certification](https://support.google.com/googleplay/answer/7165974?hl=en) is not conferred by installing a Store APK.

A future test should measure sign-in, installation and updating of a free app, reboot behavior, and regressions in Hearth operation. Stop before unapproved system modifications or broad permission grants. Use a low-value test account and inspect the device's security configuration first. A Store window opening would not prove that DRM- or integrity-sensitive apps work.
