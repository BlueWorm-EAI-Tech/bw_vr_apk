# BlueWorm VR APK

[English](./README.md) | 中文

## 一键安装（推荐）

把 `Quantum.apk` 装到 PICO 头显，两步搞定。

### 1. 连接头显

- 用 USB 线连接头显与电脑
- 头显里开启「开发者模式 → USB 调试」
- 弹出「允许 USB 调试」时点允许

### 2. 运行脚本

| 系统 | 命令 |
|---|---|
| Windows | 双击 `install_quantum_apk.bat` |
| Linux / macOS | `./install_quantum_apk.sh` |
| 任意系统（已装 Python 3） | `python install_quantum_apk.py` |

脚本会自动完成：

- 查找 adb：环境变量 `ADB` → PATH → PICO 开发者中心 / Android SDK / Unity 自带路径
- **本机没有 adb 时自动下载** Google 官方 platform-tools 到 `~/.quantum_apk_tools`，无需手动安装
- 识别已连接的头显（多台设备时会列出型号让你选）
- 安装 APK；遇到签名冲突会说明原因并询问，加 `-y` 自动卸载重装
- 安装后回读包信息，并检查 `isVrApp` 是否为 `true`（该项为 `false` 时系统不会向应用下发手柄输入）

### 常用参数

| 参数 | 说明 |
|---|---|
| `-f, --apk <路径>` | 指定 APK，默认使用脚本同目录的 `Quantum.apk` |
| `-d, --device <序列号>` | 多台设备时指定目标 |
| `-p, --package <包名>` | 目标包名，默认 `com.BlueWormEAI.Quantum` |
| `-y, --yes` | 签名冲突时自动卸载重装，不再询问 |
| `--launch` | 安装完成后立即启动应用 |
| `--no-verify` | 跳过安装后的包信息校验 |
| `--no-download` | 找不到 adb 时不自动下载 |
| `--force-download` | 忽略已有 adb，强制下载官方 platform-tools |

示例：

```bash
python install_quantum_apk.py -y --launch
```

> 前置条件：Python 3.6+。Windows 若没装 Python，双击 `.bat` 会给出明确提示。
> 下载源为 `dl.google.com`，失败会自动换 `dl-ssl.google.com` 重试；都失败时打印手动下载地址。

## 包简介

`Quantum.apk` 是 BlueWorm 机器人遥操作软件的 PICO VR 客户端。

APK 负责采集头显和手柄输入、显示机器人双目视频并发送控制数据。机械臂、
夹爪、头部和底盘等具体动作由配套机器人侧服务决定。

## 已有功能

### VR 数据与控制

- 持续采集头显、左右实体手柄的位置和姿态。
- 采集 Trigger、Grip、A/B/X/Y、左右摇杆和摇杆按键状态。
- 通过 UDP 向机器人发送 VR 姿态和手柄输入。
- 通过 ROS-TCP 发送菜单、模式、急停和复位命令。
- 支持相对/绝对控制、底盘速度档和运动模式切换。
- 打开 VR 菜单时自动暂停姿态输出，避免操作菜单时误控机器人。

### 视频与连接

- 通过 WebRTC 显示机器人左右眼双目视频。
- 显示 ROS、视频和音频链路状态。
- LAN 模式支持机器人 IP 输入、保存和局域网搜索。
- Internet 模式支持账号登录和按机器人 SN 建立连接。

## 使用前准备

- PICO 头显应为 64 位 ARM 设备，系统为 Android 10（API 29）或更高版本。
- 确保 PICO 实体手柄已配对且电量充足。
- 使用 LAN 模式时，PICO 与机器人必须接入同一局域网。
- 机器人侧必须已启动兼容的 ROS、UDP、WebRTC 和音频服务。
- 清空机器人工作区域，确认现场物理急停可用，首次操作使用低速档。

> 此 APK 不能单独完成机器人控制。机器人侧服务和网络未就绪时，
> 视频、音频或控制功能将不可用。

## 安装 PICO APK

### 1. 下载 APK

```bash
wget -O "$HOME/Downloads/Quantum.apk" \
  https://raw.githubusercontent.com/BlueWorm-EAI-Tech/bw_vr_apk/main/Quantum.apk
```

### 2. 安装 ADB

电脑需要安装 Android SDK Platform-Tools，并确保 `adb` 命令在 `PATH` 中。
Ubuntu 可执行：

```bash
sudo apt install adb
adb version
```

### 3. 开启调试模式

1. 在 PICO 中进入 **设置 > 关于本机**。
2. 连续点击软件版本号，开启开发者模式。
3. 进入 **设置 > 开发者选项**，开启 USB 调试。
4. 使用 USB Type-C 数据线连接 PICO 与电脑。
5. 戴上头显并允许 USB 调试授权。

不同 PICO 系统版本的菜单名称可能略有差异。

### 4. 使用 ADB 安装（推荐）

在电脑终端运行：

```bash
adb devices
adb install -r $HOME/Downloads/Quantum.apk
```

`adb devices` 应显示一台状态为 `device` 的设备。安装成功时，终端会显示
`Success`。

## 首次启动

1. 在 PICO 应用列表或“未知来源”列表中打开 `Quantum`。
2. 按系统提示授予相机和麦克风权限。
3. 确认应用能识别左右实体手柄。

APK 文件名为 `Quantum.apk`, 安装后的应用名称为 `Quantum`。

## 基本使用流程

### 局域网模式（推荐）

1. 先启动机器人及其 ROS、UDP、WebRTC 和音频服务。
2. 打开 VR 应用，保持首页的 **Mode: LAN**。
3. 在 **Robot IP** 中输入机器人 IP，或点击搜索。
4. 点击连接，检查 ROS、Video/WebRTC 和 Audio 状态。
5. 状态正常后，点击 **开始控制**。
6. 进入控制场景后，短按左手柄 Menu 打开 VR 菜单，在控制设置中选择低速。
7. 再次确认工作区无人、物理急停可用，然后关闭菜单恢复控制输出。

如果不知道机器人 IP，可在机器人主机运行 `hostname -I` 查看。

默认网络端口如下：

| 链路 | 默认地址 |
| --- | --- |
| ROS-TCP | `<机器人IP>:10000` |
| 左眼 WebRTC | `ws://<机器人IP>:8080/ws` |
| 右眼 WebRTC | `ws://<机器人IP>:8081/ws` |

状态灯不是程序的强制进入条件。为保证现场安全，应确认视频和控制链路正常后
再开始操作。

### 互联网模式（可选）

1. 将首页模式切换为 **Mode: Internet**。
2. 在用户配置窗口登录。
3. 选择已经绑定的机器人 SN。
4. 点击连接，连接成功后点击 **开始控制**。

互联网模式依赖账号、控制面服务和 TURN/WebRTC 服务。公网服务不可用时，
请改用 LAN 模式。

## 实体手柄操作

| 输入 | 功能 |
| --- | --- |
| 左手柄 Menu 短按 | 打开或关闭 VR 设置菜单 |
| 左摇杆按下 | 重置 VR 原点和机器人头部零位 |
| 右摇杆按下 | 循环切换底盘高、中、低速档 |
| 左摇杆 | 控制底盘平移 |
| 右摇杆左右 | 控制底盘旋转 |
| 右摇杆上下 | 控制滑台速度 |
| 左右 Trigger | 控制对应夹爪 |
| 左右 Grip | 相对模式下，按住时对应机械臂跟随手柄 |
| 左摇杆 XY齐按 | 控制左臂复位 |
| 右摇杆 AB齐按 | 控制右臂复位 |

打开 VR 设置菜单后，应用会暂停 VR 姿态发送。此时机器人不响应手柄姿态属于
正常行为。关闭菜单后，应用会恢复控制输出。

> 操作前必须确认机器人状态；不能用它替代现场物理急停装置。

## 更新与卸载

覆盖安装新版本：

```bash
adb install -r ./Quantum.apk
```

卸载应用：

```bash
adb uninstall com.BlueWormEAI.Quantum
```

卸载会清除应用保存的机器人 IP、账号和其他本地配置。

## 常见问题

### ADB 显示 `unauthorized`

戴上头显并允许 USB 调试，然后运行：

```bash
adb kill-server
adb start-server
adb devices
```

### 安装提示 `INSTALL_FAILED_UPDATE_INCOMPATIBLE`

设备中已安装相同包名但签名不同的版本。卸载旧版后重新安装：

```bash
adb uninstall com.BlueWormEAI.Quantum
adb install ./Quantum.apk
```

### 无法发现或连接机器人

- 确认 PICO 与机器人位于同一局域网，且 IP 地址填写正确。
- 确认机器人侧 ROS-TCP 服务监听 `10000` 端口。
- 确认左右眼 WebRTC 服务监听 `8080` 和 `8081` 端口。
- 检查路由器的客户端隔离设置和机器人防火墙。
- 搜索失败时，直接输入机器人 IP 再连接。

### 有连接状态但没有视频或控制

连接状态只表示部分探测成功，不代表视频首帧或控制链路已经就绪。分别检查
机器人侧 WebRTC、ROS、UDP 和音频服务，并确认应用权限已经授予。

## 版本信息

- 发布文件：`Quantum.apk`
- 应用名称：`Quantum`
- 构建类型：0508 Original / 非 Wrist / 实体手柄控制
- 应用版本：`0.0.1`（versionCode `1`）
- Android 包名：`com.BlueWormEAI.Quantum`
- 文件大小：`66,604,311` 字节（约 63.52 MiB）
- SHA-256：
  `ec882d7bf298e50b497fcab16bf573958bf1d1a62fe837b51a950affd7fab77c`

校验 APK：

```bash
sha256sum ./Quantum.apk
# 预期输出以此哈希开头：

ec882d7bf298e50b497fcab16bf573958bf1d1a62fe837b51a950affd7fab77c
```

## 许可证

本项目采用 MIT License。详情请参阅 [LICENSE](LICENSE)。

## 联系方式

- 邮箱：[chenpeel@foxmail.com](mailto:chenpeel@foxmail.com)
