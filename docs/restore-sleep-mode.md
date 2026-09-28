# Restore Hearth Sleep Mode after liberation

Hardware qualification date: 2026-09-28

## Symptom

After owner-access/liberation changes, Hearth's **Display Settings → Sleep Mode → Schedule** control can become unavailable and show:

> This feature requires a software update. Please leave your Display plugged in overnight in order to update.

The display then remains awake even though the previous schedule is still stored.

## Root cause

The stock privileged HMF package remains installed at `/system_ext/priv-app/HMFService/HMFService.apk`, but the display scheduler depends specifically on:

`com.hearth.hmf/.PrivilegedService`

Enabling `com.hearth.hmf` alone can start the HMF process without starting that component. In that state the stock Hearth app's `PrivilegedSdk` receives a null `IPrivilegedService`, reports the scheduler unsupported, and disables the Schedule UI.

When `PrivilegedService` starts it registers the stock Binder service:

`hearth_ipc: [com.hearth.hmf.aidl.IPrivilegedService]`

The stock Schedule UI then becomes available again after Hearth is restarted.

## Reversible restoration

From an authorized ADB shell on your own display:

```sh
pm enable com.hearth.hmf
am startservice -n com.hearth.hmf/.PrivilegedService
service list | grep hearth_ipc
am force-stop com.nativeapp
monkey -p com.nativeapp -c android.intent.category.LAUNCHER 1
```

Expected Binder registration:

```text
hearth_ipc: [com.hearth.hmf.aidl.IPrivilegedService]
```

Then open **Display Settings → Sleep Mode** and verify the stock Schedule control and saved times are visible.

## What the stock scheduler does

Reverse engineering of the installed HMF implementation found that it stores state in Android Global settings:

- `hearth_display_scheduler_active`
- `hearth_display_scheduler_start`
- `hearth_display_scheduler_stop`

The start/stop values are seconds since midnight. HMF uses `AlarmManager.setExact()`, reacts to time/timezone changes, and uses `PowerManager.goToSleep()` / `wakeUp()`. While inside the sleep window, touching the display wakes it and HMF schedules a return to sleep after 300,000 ms (five minutes).

On the qualified unit, the original schedule survived liberation and was recovered without rewriting its values.

## Qualification notes

- Package enable alone was insufficient.
- Explicit `PrivilegedService` startup restored `hearth_ipc`.
- Restarting the stock Hearth app after Binder registration restored the Schedule UI.
- The existing wake alarm was observed registered under HMF.
- Persistent boot restoration still requires reboot qualification. Do not describe it as reboot-proven until that test is complete.
