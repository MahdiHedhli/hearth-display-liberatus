# Enable developer options and pair ADB

This gets your computer talking to the display. It does not disable Hearth, change the launcher, or restore the navigation bar yet.

The menu instructions are adapted from [mbazos/hearth-hacking](https://github.com/mbazos/hearth-hacking/blob/b540ba0223169b3adaf426bc2695e67823e24b02/README.md). Android's [developer-options guide](https://developer.android.com/studio/debug/dev-options) describes the build-number step, and its [ADB guide](https://developer.android.com/tools/adb) explains pairing.

## 1. Get to Android Settings

Use the display's existing route to Android Settings, such as an available exit control or an already-installed launcher. The community repository links this [menu walkthrough](https://youtube.com/shorts/VGBEjFyY7hs).

Some Hearth software versions no longer show the same exit control. This repository has no verified universal escape gesture for those versions. If you cannot reach Android Settings and do not already have an authorized ADB connection, stop here. The later commands cannot create the first connection by themselves.

## 2. Install the computer tools

Download [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) from Google and extract the archive. You do not need the full Android Studio installation.

Open a terminal in the extracted `platform-tools` directory. For this terminal session, add that directory to the executable search path:

PowerShell on Windows:

```powershell
$env:Path = "$PWD;$env:Path"
adb version
```

Terminal on macOS or Linux:

```sh
export PATH="$PWD:$PATH"
adb version
```

The version command should print Android Debug Bridge information. If it says the command cannot be found, fix the path before proceeding.

Use a trusted network where the computer and display can reach each other. Guest-network isolation or blocked multicast discovery can prevent a connection even when both devices have internet access.

## 3. Reveal developer options

On the display, open Android **Settings**, then **About tablet** or **About phone**. Some builds put this under **System**.

Find **Build number** and tap it seven times. Enter the device PIN if asked. Return to **System**, then open **Developer options**. The exact menu labels depend on the build.

Turn on the developer-options switch if there is one. Enable **Wireless debugging**. Some customized builds also require **USB debugging** to be enabled in this menu; it is not inherently a requirement of Android's paired wireless workflow.

When Android asks whether to allow wireless debugging on this network, approve your trusted network. Only select **Always allow** on a network you control.

## 4. Pair the computer

Open **Wireless debugging**, then **Pair device with pairing code**. Leave that dialog open.

It shows an address with a pairing port and a short-lived code. In your terminal, replace `DEVICE_IP` and `PAIRING_PORT` with the values from that dialog:

```text
adb pair DEVICE_IP:PAIRING_PORT
```

Enter the code when ADB asks for it. Keep the code out of shell history, screenshots, public issues, and this repository.

After successful pairing, close the pairing dialog and read **IP address & Port** on the main Wireless debugging screen. This is the connection address, which may use a different port:

```text
adb connect DEVICE_IP:CONNECTION_PORT
adb devices -l
```

The Hearth entry should end up in the `device` state. An `offline` entry is not a working connection. Pairing authorizes a computer; it does not guarantee that debugging stays enabled after a reboot or vendor-policy change.

If the device already connects successfully with an existing authorization, there is no need to pair again just because a new pairing attempt failed.

## 5. Select exactly one device

Every device-changing command in this guide uses an explicit target. Copy the Hearth's first-column entry from `adb devices -l`. It may be an address and port or a discovered wireless service name.

Set this variable in the same terminal you will use for the rest of the guide:

PowerShell:

```powershell
$Hearth = 'HEARTH_TARGET'
```

macOS or Linux:

```sh
Hearth='HEARTH_TARGET'
```

Replace `HEARTH_TARGET` with that entry. Do not leave the placeholder in place.

Both shells can then run:

```sh
adb -s "$Hearth" get-state
adb -s "$Hearth" shell id
adb -s "$Hearth" shell getprop ro.product.device
adb -s "$Hearth" shell getprop ro.product.model
adb -s "$Hearth" shell getprop ro.build.version.release
adb -s "$Hearth" shell getprop ro.build.type
adb -s "$Hearth" shell getprop ro.debuggable
```

On the tested unit, ordinary access returned `uid=2000(shell)`. Its software identifiers included `rk3566_r` and `rk3568`; those strings alone do not identify the physical chip. The build was Android 11, `userdebug`, with `ro.debuggable=1`.

Keep actual device identifiers private. Use the package checks in the [navigation guide](native-navigation.md) to establish whether its method applies.

## A changing port is normal in this workflow

Restarting the ADB daemon can change the connection port. Check the main Wireless debugging screen again or run:

```sh
adb mdns services
adb devices -l
```

The `_adb-tls-pairing._tcp` service is for pairing. The `_adb-tls-connect._tcp` service is for an authorized debugging connection. Use the current connection address, reconnect if needed, and update `$Hearth` before another targeted command.

If discovery is empty, that alone does not prove debugging is off. Check the on-screen address and local network reachability. Do not solve this by forwarding an ADB port through your internet router.

Continue with [Restore the native navigation bar](native-navigation.md).
