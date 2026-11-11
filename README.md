# BlueWorm VR APK

English | [中文](./README_zh.md)

## Overview

`Quantum.apk` is the PICO VR client for BlueWorm robot
teleoperation.

The APK captures headset and controller input, displays stereo robot video,
and sends control data. The paired robot-side services determine the exact
behavior of the arms, grippers, head, and mobile base.

## Features

### VR Data and Control

- Continuously captures the position and orientation of the headset and both
  physical controllers.
- Captures Trigger, Grip, A/B/X/Y, both joysticks, and joystick button states.
- Sends VR poses and controller input to the robot over UDP.
- Sends menu, mode, emergency-stop, and reset commands over ROS-TCP.
- Supports relative and absolute control, base speed levels, and motion modes.
- Pauses pose output while the VR menu is open to prevent unintended motion.

### Video and Connectivity

- Displays the robot's left-eye and right-eye video streams over WebRTC.
- Shows ROS, video, and audio connection status.
- LAN mode supports manual robot IP entry, saved IPs, and local network search.
- Internet mode supports account login and connection by robot serial number.

## Prerequisites

- Use a 64-bit ARM PICO headset running Android 10 (API 29) or later.
- Pair both physical PICO controllers and make sure they have enough charge.
- For LAN mode, connect the PICO headset and robot to the same local network.
- Start the compatible ROS, UDP, WebRTC, and audio services on the robot.
- Clear the robot workspace, verify the physical emergency stop, and use the
  low-speed setting for the first operation.

> This APK cannot control a robot by itself. Video, audio, and control features
> remain unavailable until the robot-side services and network are ready.

## Install the PICO APK

### 1. Download the APK

```bash
wget -O "$HOME/Downloads/Quantum.apk" \
  https://raw.githubusercontent.com/BlueWorm-EAI-Tech/bw_vr_apk/main/Quantum.apk
```

### 2. Install ADB

Install Android SDK Platform-Tools and make sure `adb` is available in your
`PATH`. On Ubuntu, run:

```bash
sudo apt install adb
adb version
```

### 3. Enable Debugging

1. On the PICO headset, open **Settings > About Device**.
2. Select the software version repeatedly to enable developer mode.
3. Open **Settings > Developer Options** and enable USB debugging.
4. Connect the PICO headset to the computer with a USB Type-C data cable.
5. Put on the headset and approve the USB debugging prompt.

Menu names may vary slightly between PICO system versions.

### 4. Install with ADB (Recommended)

Run the following commands on the computer:

```bash
adb devices
adb install -r $HOME/Downloads/Quantum.apk
```

`adb devices` should list the headset with the status `device`. A successful
installation prints `Success`.

## First Launch

1. Open `Quantum` from the PICO app library or **Unknown Sources**.
2. Allow camera and microphone access when prompted.
3. Confirm that the app detects both physical controllers.

The APK filename is `Quantum.apk` and the installed app name is `Quantum`.

## Basic Workflow

### LAN Mode (Recommended)

1. Start the robot and its ROS, UDP, WebRTC, and audio services.
2. Open the VR app and keep **Mode: LAN** selected on the home screen.
3. Enter the robot IP in **Robot IP**, or use the search control.
4. Connect and check the ROS, Video/WebRTC, and Audio status indicators.
5. When the connections are ready, select **Start Control (`开始控制`)**.
6. In the control scene, briefly press the left controller Menu button to open
   the VR menu. Under **Control Settings (`控制设置`)**, select
   **Low Speed (`低速`)**.
7. Check that the workspace is clear and the physical emergency stop is ready,
   then close the menu to resume control output.

If the robot IP is unknown, run `hostname -I` on the robot computer.

Default endpoints:

| Connection | Default endpoint |
| --- | --- |
| ROS-TCP | `<ROBOT_IP>:10000` |
| Left-eye WebRTC | `ws://<ROBOT_IP>:8080/ws` |
| Right-eye WebRTC | `ws://<ROBOT_IP>:8081/ws` |

The status indicators are not a software-enforced entry requirement. For safe
operation, verify the video and control links before controlling the robot.

### Internet Mode (Optional)

1. Switch the home screen to **Mode: Internet**.
2. Sign in from the user configuration window.
3. Select a robot that is already bound to your account by serial number.
4. Connect, then select **Start Control (`开始控制`)** after the connection
   succeeds.

Internet mode depends on the account, control-plane, and TURN/WebRTC services.
Use LAN mode when the public services are unavailable.

## Physical Controller Mapping

| Input | Action |
| --- | --- |
| Briefly press left Menu | Open or close the VR settings menu |
| Press left joystick | Reset the VR origin and robot head zero position |
| Press right joystick | Cycle through high, medium, and low base speed |
| Move left joystick | Translate the mobile base |
| Move right joystick horizontally | Rotate the mobile base |
| Move right joystick vertically | Control the linear slide speed |
| Left/right Trigger | Control the corresponding gripper |
| Left/right Grip | In relative mode, hold to move the corresponding arm |
| Press left X + Y together | Reset the left arm |
| Press right A + B together | Reset the right arm |

Opening the VR settings menu pauses VR pose transmission. The robot not
responding to controller poses while the menu is open is expected behavior.
Closing the menu resumes control output.

> Always verify the robot state before operating it. The software controls do
> not replace the physical emergency-stop device.

## Update and Uninstall

Install a newer build while preserving application data:

```bash
adb install -r ./Quantum.apk
```

Uninstall the app:

```bash
adb uninstall com.BlueWormEAI.Quantum
```

Uninstalling clears saved robot IPs, account data, and other local settings.

## Troubleshooting

### ADB Shows `unauthorized`

Put on the headset, approve USB debugging, and run:

```bash
adb kill-server
adb start-server
adb devices
```

### Installation Fails with `INSTALL_FAILED_UPDATE_INCOMPATIBLE`

An installed app uses the same package name but a different signature.
Uninstall it before installing this APK:

```bash
adb uninstall com.BlueWormEAI.Quantum
adb install ./Quantum.apk
```

### The App Cannot Find or Connect to the Robot

- Confirm that the PICO headset and robot are on the same local network.
- Confirm that the entered robot IP is correct.
- Confirm that ROS-TCP listens on port `10000`.
- Confirm that the left-eye and right-eye WebRTC services listen on ports
  `8080` and `8081`.
- Check client isolation on the router and the robot firewall.
- If search fails, enter the robot IP manually and connect again.

### A Status Indicator Is Active but Video or Control Does Not Work

A connection indicator only confirms that part of the probe succeeded. It does
not guarantee that the first video frame or control link is ready. Check the
robot-side WebRTC, ROS, UDP, and audio services separately, and verify that the
app permissions have been granted.

## Version Information

- Release file: `Quantum.apk`
- Installed app name: `Quantum`
- Build type: 0508 Original / non-Wrist / physical-controller input
- App version: `0.0.1` (versionCode `1`)
- Android package: `com.BlueWormEAI.Quantum`
- File size: `66,604,311` bytes (approximately 63.52 MiB)
- SHA-256:
  `ec882d7bf298e50b497fcab16bf573958bf1d1a62fe837b51a950affd7fab77c`

Verify the APK:

```bash
sha256sum ./Quantum.apk
# Expected hash prefix:

ec882d7bf298e50b497fcab16bf573958bf1d1a62fe837b51a950affd7fab77c
```

## License

This project is licensed under the MIT License. See
[LICENSE](LICENSE) for details.

## Contact

- Email: [chenpeel@foxmail.com](mailto:chenpeel@foxmail.com)
