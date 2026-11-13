#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键安装 Quantum.apk 到 PICO 头显。

用法（Windows / Linux / macOS 通用）：
    python install_quantum_apk.py                # 装同目录下的 Quantum.apk
    python install_quantum_apk.py -y             # 遇到签名冲突自动卸载重装
    python install_quantum_apk.py --launch       # 装完直接启动
    python install_quantum_apk.py -f other.apk   # 指定 APK

依赖：仅需 Python 3.6+ 和 adb（脚本会自动在常见路径里找 adb）。
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

DEFAULT_APK = "Quantum.apk"
DEFAULT_PKG = "com.BlueWormEAI.Quantum"

# 常见 adb 位置（构建于运行时，避免占位符展开踩坑）
def windows_adb_candidates():
    appdata = os.environ.get("APPDATA", "")
    localappdata = os.environ.get("LOCALAPPDATA", "")
    profile = os.environ.get("USERPROFILE", "")

    paths = []
    if appdata:
        paths.append(os.path.join(appdata, "PICO_Developer_Center_Downloads", "cn", "adb", "platform-tools", "adb.exe"))
        paths.append(os.path.join(appdata, "PICO_Developer_Center_Downloads", "adb", "platform-tools", "adb.exe"))
    if localappdata:
        paths.append(os.path.join(localappdata, "Android", "Sdk", "platform-tools", "adb.exe"))
    if profile:
        paths.append(os.path.join(profile, "AppData", "Local", "Android", "Sdk", "platform-tools", "adb.exe"))
    paths.extend([
        r"D:\UnityEditors\Editor\Data\PlaybackEngines\AndroidPlayer\SDK\platform-tools\adb.exe",
        r"C:\Program Files\Unity\Hub\Editor\Data\PlaybackEngines\AndroidPlayer\SDK\platform-tools\adb.exe",
    ])
    return paths


def linux_adb_candidates():
    return [
        os.path.expanduser("~/Android/Sdk/platform-tools/adb"),
        os.path.expanduser("~/android-sdk/platform-tools/adb"),
        "/usr/local/bin/adb",
        "/usr/bin/adb",
        "/opt/android-sdk/platform-tools/adb",
        "/opt/android/platform-tools/adb",
    ]


def say(msg):
    print(msg, flush=True)


def die(msg, code=1):
    print("错误：" + msg, file=sys.stderr, flush=True)
    sys.exit(code)


PLATFORM_TOOLS_FILES = {
    "Windows": "platform-tools-latest-windows.zip",
    "Linux": "platform-tools-latest-linux.zip",
    "Darwin": "platform-tools-latest-darwin.zip",
}

PLATFORM_TOOLS_BASE = "https://dl.google.com/android/repository/"
PLATFORM_TOOLS_MIRRORS = [
    "https://dl.google.com/android/repository/",
    "https://dl-ssl.google.com/android/repository/",
]


def tools_dir():
    override = os.environ.get("QUANTUM_APK_TOOLS_DIR")
    if override:
        return os.path.expanduser(override)
    return os.path.join(os.path.expanduser("~"), ".quantum_apk_tools")


def adb_name():
    return "adb.exe" if os.name == "nt" else "adb"


def cached_adb():
    """已经下载过的 platform-tools。"""
    path = os.path.join(tools_dir(), "platform-tools", adb_name())
    return path if os.path.isfile(path) else None


def download_progress(count, block_size, total_size):
    if total_size <= 0:
        return
    done = min(100, int(count * block_size * 100 / total_size))
    if done % 10 == 0:
        say("  下载中…… %d%%" % done)


def download_platform_tools():
    """下载并解压官方 platform-tools，返回 adb 路径。"""
    import platform
    import zipfile
    import urllib.request

    system = platform.system()
    filename = PLATFORM_TOOLS_FILES.get(system)
    if not filename:
        die("当前系统（%s）没有对应的 platform-tools 下载包，请手动安装 adb。" % system)

    target_dir = tools_dir()
    os.makedirs(target_dir, exist_ok=True)
    zip_path = os.path.join(target_dir, filename)

    say("本机没找到 adb，自动下载 Android Platform-Tools……")
    say("  平台：%s" % system)
    say("  缓存目录：%s" % target_dir)

    last_error = None
    for base in PLATFORM_TOOLS_MIRRORS:
        url = base + filename
        try:
            say("  源：%s" % url)
            with urllib.request.urlopen(url, timeout=60) as response, open(zip_path, "wb") as out_file:
                total = int(response.headers.get("Content-Length") or 0)
                downloaded = 0
                while True:
                    chunk = response.read(1024 * 256)
                    if not chunk:
                        break
                    out_file.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = int(downloaded * 100 / total)
                        if pct % 20 == 0:
                            say("  下载中…… %d%%" % pct)
            last_error = None
            break
        except Exception as exc:  # noqa: BLE001 - 任何网络问题都换源重试
            last_error = exc
            say("  该源失败：%s" % exc)

    if last_error is not None:
        die(
            "自动下载 platform-tools 失败：%s\n"
            "请手动下载并解压，然后把 adb 所在目录加入 PATH，或设置环境变量 ADB 指向 adb：\n"
            "  %s%s" % (last_error, PLATFORM_TOOLS_BASE, filename)
        )

    say("  解压……")
    try:
        with zipfile.ZipFile(zip_path) as archive:
            archive.extractall(target_dir)
    except Exception as exc:  # noqa: BLE001
        die("解压失败：%s" % exc)

    try:
        os.remove(zip_path)
    except OSError:
        pass

    adb_path = os.path.join(target_dir, "platform-tools", adb_name())
    if not os.path.isfile(adb_path):
        die("下载完成但没有找到 adb，请检查 %s" % target_dir)

    if os.name != "nt":
        platform_tools_dir = os.path.dirname(adb_path)
        for entry in os.listdir(platform_tools_dir):
            full = os.path.join(platform_tools_dir, entry)
            if os.path.isfile(full):
                try:
                    os.chmod(full, 0o755)
                except OSError:
                    pass

    say("  完成：%s" % adb_path)
    return adb_path


def ensure_adb(allow_download=True):
    """优先用已有的 adb；没有则自动下载。"""
    found = find_adb(raise_on_missing=False)
    if found:
        return found

    cached = cached_adb()
    if cached:
        say("使用已缓存的 platform-tools：%s" % cached)
        return cached

    if not allow_download:
        die(
            "找不到 adb，且已禁用自动下载（--no-download）。\n"
            "请安装 Android Platform-Tools 或设置环境变量 ADB。"
        )

    return download_platform_tools()


def expand(path):
    return os.path.expandvars(os.path.expanduser(path))


def find_adb(raise_on_missing=True):
    """按环境变量 -> PATH -> 常见安装路径的顺序查找 adb。"""
    env_adb = os.environ.get("ADB")
    if env_adb and os.path.isfile(expand(env_adb)):
        return expand(env_adb)

    which = shutil.which("adb")
    if which:
        return which

    candidates = windows_adb_candidates() if os.name == "nt" else linux_adb_candidates()
    for path in candidates:
        if path and os.path.isfile(path):
            return path

    if not raise_on_missing:
        return None

    die(
        "找不到 adb。请安装 Android Platform-Tools，或设置环境变量 ADB 指向 adb 可执行文件。\n"
        "  Windows 常见位置：%APPDATA%\\PICO_Developer_Center_Downloads\\cn\\adb\\platform-tools\\adb.exe\n"
        "  Linux 常见位置：~/Android/Sdk/platform-tools/adb"
    )


def run(cmd, timeout=180):
    """执行命令，返回 (returncode, 合并输出)。"""
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
        out = proc.stdout.decode("utf-8", errors="replace")
        return proc.returncode, out.strip()
    except subprocess.TimeoutExpired:
        return 124, "命令超时：%s" % " ".join(cmd)
    except OSError as exc:
        return 127, "无法执行 %s：%s" % (cmd[0], exc)


def list_devices(adb):
    code, out = run([adb, "devices"], timeout=60)
    if code != 0:
        die("adb devices 执行失败：\n" + out)

    devices = []
    for line in out.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices") or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
        elif len(parts) >= 2:
            say("跳过设备 %s（状态：%s，请在头显里允许 USB 调试）" % (parts[0], parts[1]))
    return devices


def pick_device(adb, devices, wanted):
    if wanted:
        if wanted not in devices:
            die("指定的设备 %s 不在已连接列表里：%s" % (wanted, ", ".join(devices) or "无"))
        return wanted

    if not devices:
        die(
            "没有检测到设备。请确认：\n"
            "  1. 头显已用 USB 连接到电脑\n"
            "  2. 头显里已开启「开发者模式 → USB 调试」\n"
            "  3. 头显里弹出的「允许 USB 调试」已点允许"
        )

    if len(devices) == 1:
        return devices[0]

    say("检测到多个设备：")
    for idx, serial in enumerate(devices, 1):
        code, model = run([adb, "-s", serial, "shell", "getprop", "ro.product.model"], timeout=30)
        say("  %d) %s  型号=%s" % (idx, serial, model if code == 0 else "未知"))

    if not sys.stdin.isatty():
        die("多个设备且非交互运行，请用 --device <序列号> 指定目标。")

    while True:
        choice = input("请输入序号选择设备：").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(devices):
            return devices[int(choice) - 1]
        say("输入无效，请重新输入。")


def device_label(adb, serial):
    code, model = run([adb, "-s", serial, "shell", "getprop", "ro.product.model"], timeout=30)
    code2, android = run([adb, "-s", serial, "shell", "getprop", "ro.build.version.release"], timeout=30)
    model = model if code == 0 else "未知型号"
    android = android if code2 == 0 else "?"
    return "%s (Android %s)" % (model, android)


def is_signature_conflict(output):
    markers = (
        "INSTALL_FAILED_UPDATE_INCOMPATIBLE",
        "signatures do not match",
        "INSTALL_FAILED_ALREADY_EXISTS",
    )
    return any(m in output for m in markers)


def install_apk(adb, serial, apk, package, auto_uninstall):
    say("开始安装：%s" % apk)
    started = time.time()
    code, out = run([adb, "-s", serial, "install", "-r", apk], timeout=600)
    say(out)

    if code == 0 and "Success" in out:
        say("安装成功，用时 %.1f 秒" % (time.time() - started))
        return True

    if not is_signature_conflict(out):
        return False

    say("")
    say("设备上已有的 %s 用不同证书签名，无法直接覆盖安装。" % package)
    say("要装新包只能先卸载旧包，这会清除该应用的本地数据（登录状态、设置）。")

    if not auto_uninstall:
        if not sys.stdin.isatty():
            die("签名冲突且非交互运行。加 -y 参数可自动卸载重装。")
        answer = input("是否卸载旧包并继续？输入 yes 继续：").strip().lower()
        if answer not in ("y", "yes", "是"):
            die("已取消，未做任何修改。", code=2)

    say("卸载旧包：%s" % package)
    code_u, out_u = run([adb, "-s", serial, "uninstall", package], timeout=180)
    say(out_u)
    if code_u != 0 and "Success" not in out_u:
        say("卸载返回异常，仍尝试继续安装……")

    say("重新安装：%s" % apk)
    code2, out2 = run([adb, "-s", serial, "install", apk], timeout=600)
    say(out2)
    return code2 == 0 and "Success" in out2


def verify_install(adb, serial, package):
    code, out = run([adb, "-s", serial, "shell", "dumpsys", "package", package], timeout=60)
    if code != 0 or "Unable to find package" in out:
        say("警告：查询不到包信息，安装可能未生效。")
        return False

    version = ""
    updated = ""
    is_vr = ""
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("versionName=") and not version:
            version = line.split("=", 1)[1]
        elif line.startswith("lastUpdateTime=") and not updated:
            updated = line.split("=", 1)[1]
        elif line.startswith("isVrApp:"):
            is_vr = line.split(":", 1)[1].strip()

    say("包名：%s" % package)
    say("版本：%s" % (version or "?"))
    say("更新时间：%s" % (updated or "?"))
    if is_vr:
        say("VR 应用标记：%s %s" % (is_vr, "（正常）" if is_vr == "true" else "（异常：系统不会下发手柄输入）"))
    return True


def launch_app(adb, serial, package):
    say("启动应用：%s" % package)
    code, out = run(
        [adb, "-s", serial, "shell", "monkey", "-p", package, "-c", "android.intent.category.LAUNCHER", "1"],
        timeout=60,
    )
    if code == 0:
        say("已发送启动指令。")
    else:
        say("启动失败：%s" % out)


def main():
    parser = argparse.ArgumentParser(
        description="一键安装 Quantum.apk 到 PICO 头显（Windows / Linux / macOS）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python install_quantum_apk.py\n"
            "  python install_quantum_apk.py -y --launch\n"
            "  python install_quantum_apk.py -d PA921JMGJ9110098G -f Builds/Quantum.apk\n"
        ),
    )
    parser.add_argument("-f", "--apk", default=None, help="APK 路径，默认使用脚本同目录下的 %s" % DEFAULT_APK)
    parser.add_argument("-d", "--device", default=None, help="设备序列号（多台设备时指定）")
    parser.add_argument("-p", "--package", default=DEFAULT_PKG, help="目标包名，默认 %s" % DEFAULT_PKG)
    parser.add_argument("-y", "--yes", action="store_true", help="遇到签名冲突时自动卸载重装，不再询问")
    parser.add_argument("--launch", action="store_true", help="安装完成后立即启动应用")
    parser.add_argument("--no-verify", action="store_true", help="跳过安装后的包信息校验")
    parser.add_argument("--no-download", action="store_true", help="找不到 adb 时不自动下载 platform-tools")
    parser.add_argument("--force-download", action="store_true", help="忽略已有的 adb，强制下载官方 platform-tools")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    apk = args.apk or os.path.join(script_dir, DEFAULT_APK)
    apk = os.path.abspath(os.path.expanduser(apk))

    if not os.path.isfile(apk):
        die("找不到 APK：%s" % apk)

    size_mb = os.path.getsize(apk) / (1024.0 * 1024.0)
    say("APK：%s（%.1f MB）" % (apk, size_mb))

    adb = download_platform_tools() if args.force_download else ensure_adb(allow_download=not args.no_download)
    say("adb：%s" % adb)

    say("启动 adb 服务……")
    run([adb, "start-server"], timeout=60)

    devices = list_devices(adb)
    serial = pick_device(adb, devices, args.device)
    say("目标设备：%s  %s" % (serial, device_label(adb, serial)))
    say("")

    if not install_apk(adb, serial, apk, args.package, args.yes):
        die("安装失败。常见原因：USB 连接不稳、存储空间不足、APK 与设备架构不符。")

    if not args.no_verify:
        say("")
        verify_install(adb, serial, args.package)

    if args.launch:
        say("")
        launch_app(adb, serial, args.package)

    say("")
    say("完成。")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已中断。")
        sys.exit(130)
