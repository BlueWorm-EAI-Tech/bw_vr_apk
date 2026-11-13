#!/usr/bin/env bash
# 一键安装 Quantum.apk 到 PICO 头显（Linux / macOS / Git Bash）
set -euo pipefail

cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
    exec python3 ./install_quantum_apk.py "$@"
elif command -v python >/dev/null 2>&1; then
    exec python ./install_quantum_apk.py "$@"
else
    echo "未找到 Python 3，请先安装 Python 3.6+。" >&2
    echo "或者直接运行：adb install -r Quantum.apk" >&2
    exit 1
fi
