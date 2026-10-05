# HMF maintenance during scheduled screen-off time

Status, October 5, 2026: **controller policy and durable journal are host-tested; the Android adapters, installation and real maintenance cycle are not qualified. Do not treat this as an installation recipe or a completed device feature.**

## Intended behavior

Keep stock `com.hearth.hmf/.PrivilegedService` available for the existing display scheduler and `hearth_ipc`. Admit the broader `com.hearth.hmf/.HMFService` only while the display is actually OFF inside the configured stock sleep window. Begin ending maintenance before the configured wake boundary, preserve any in-flight update, and restore owner navigation and debugging preferences once management is safely quiescent.

The host controller uses a five-minute prewake lead by default. It first requires a verified suspend-capable alarm and one minute of fresh screen-OFF observations. A manual blackout outside the stock sleep schedule is not a maintenance window. Equal schedule boundaries do not enable maintenance.

An early touch-wake closes maintenance for the rest of that scheduled window. It does not repeatedly restart management when the panel returns to sleep. The normal scheduler still owns touch wake and scheduled display wake.

## Why this is not simply two start/stop commands

Read-only inspection found both HMF Android services in the same system-UID process. Killing that process or force-stopping the whole package can also remove the working power scheduler. A process being present is not proof that a particular service is active, and a service stop returning success is not proof that updater threads or policy callbacks have stopped.

The management service handles genuine vendor updates as well as appliance policy. Before enabling this controller, its Android adapter must establish a way to stop admission of new work without interrupting an existing update. It must positively observe application and firmware update state and verify worker quiescence. No log output, no package-install session, or no visible download is not enough to establish IDLE.

If an update is downloading, installing, waiting for reboot, or its state is unknown at the prewake deadline, the controller holds rather than killing it. Morning restoration may therefore be delayed. Update integrity takes precedence over a promised wall-clock completion time.

## Restoration order

The host-tested order is: close new admission; wait for verified update IDLE and worker quiescence; stop only the management service; preserve or recover the stock power service; restore navigation, developer options and USB debugging; honor only an existing wireless-debugging lease. Owner-access processes that might launch UI are recovered only after the screen is actually ON.

Wireless ADB is not permanently enabled by the design. An already-approved, same-boot lease may be restored for its remaining duration, with a maximum of 30 minutes. A restart cannot create or extend it. Pairing keys and trust state are not modified.

## Correct stock schedule units

The inspected firmware stores these Android Global values:

- `hearth_display_scheduler_active`
- `hearth_display_scheduler_start`
- `hearth_display_scheduler_stop`

Start and stop are **milliseconds since midnight**, not seconds. The earlier restoration guide's seconds description was incorrect. The inspected HMF alarm construction uses the hour and minute. An implementation must bind to the actual device timezone and stored stop value, not infer an exact wake time from a broader range shown in the UI. Do not assume every firmware uses the same representation.

The host model covers crossing midnight, same-day windows, schedule edits, timezone changes, DST gaps and overlaps, early touch wake, and reboot/clock-rollback closure. The production alarm and firmware behavior still require device tests.

## Crash and update boundaries

The host controller uses an exclusive writer lock and a private durable journal. An action is recorded before it executes, the platform is sampled again before application, and its actual effect must be read back. An unknown or failed outcome latches a fault instead of replaying privileged work.

A firmware update can replace the startup hook itself. No controller can promise to restore access automatically when the code that starts it has been removed. Keep an independently qualified recovery route, retain rollback material, and revalidate the firmware-specific bindings after an update. Do not spoof vendor cohorts, alter assigned releases, bypass signatures, or weaken SELinux.

## Qualification record

The independent host suite passed 140,821 policy/controller assertions and 307 journal assertions. The policy suite includes a matrix of 194,400 synthetic snapshots; these counts overlap and are not separate hardware tests. Tests cover admission/stop/restoration invariants, unknown update states, concurrent writers, crash reservations, freshness checks, corrupted journals, symlink/hardlink rejection and durable reopen. They do not contact a display or vendor API.

Still required: current HMF lifecycle review, non-interrupting admission, updater/worker observation, component-only teardown, protected restoration binding, suspend alarm delivery, Android journal testing, boot recovery, an actual night cycle and real update/reboot qualification. Production enablement remains blocked on these items.

## Related material and API references

The [stock Sleep Mode restoration](restore-sleep-mode.md) is a separate, previously observed repair. It does not establish update-preserving management isolation. See the [test record](test-record.md) for hardware versus inspected-code results.

Android documents the differing alarm behavior under power saving in [Schedule alarms](https://developer.android.com/develop/background-work/services/alarms). A native wake-alarm alternative has its own capability and clock-change requirements, described in [timerfd_create](https://man7.org/linux/man-pages/man2/timerfd_create.2.html). Neither API reference establishes a qualified Hearth implementation.
