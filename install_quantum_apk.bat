@echo off
chcp 65001 >nul
setlocal

rem 一键安装 Quantum.apk 到 PICO 头显（Windows 双击运行）

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0install_quantum_apk.py" %*
    goto :end
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0install_quantum_apk.py" %*
    goto :end
)

echo 未找到 Python 3，请先安装 Python 3.6+ 并加入 PATH。
echo 或者直接运行：adb install -r "%~dp0Quantum.apk"

:end
echo.
pause
