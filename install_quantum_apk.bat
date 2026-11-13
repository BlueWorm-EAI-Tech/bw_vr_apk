@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "APK=%~dp0Quantum.apk"
set "PKG=com.BlueWormEAI.Quantum"
set "AUTOYES=0"
set "DOLAUNCH=0"

:parse
if "%~1"=="" goto afterparse
if /i "%~1"=="-y"        set "AUTOYES=1"
if /i "%~1"=="/y"        set "AUTOYES=1"
if /i "%~1"=="--yes"     set "AUTOYES=1"
if /i "%~1"=="--launch"  set "DOLAUNCH=1"
if /i "%~1"=="-f" (
    shift
    if not "%~1"=="" set "APK=%~f1"
)
shift
goto parse
:afterparse

if not exist "%APK%" (
    echo ERROR: APK not found: %APK%
    goto fail
)

echo APK: %APK%
echo.

call :find_adb
if not defined ADBEXE call :download_adb
if not defined ADBEXE (
    echo ERROR: could not locate or download adb.
    goto fail
)

echo adb: %ADBEXE%
echo Starting adb server...
"%ADBEXE%" start-server >nul 2>nul

set "DEV="
set "COUNT=0"
for /f "skip=1 tokens=1,2" %%a in ('""%ADBEXE%" devices" 2^>nul') do (
    if /i "%%b"=="device" (
        set /a COUNT+=1
        set "DEV=%%a"
        set "LAST=%%a"
        if !COUNT!==1 set "FIRST=%%a"
    )
)

if "%COUNT%"=="0" (
    echo.
    echo ERROR: no device detected. Check:
    echo   1. headset connected by USB
    echo   2. Developer Mode - USB Debugging enabled
    echo   3. allowed the "USB debugging" prompt on the headset
    goto fail
)
if not "%COUNT%"=="1" (
    echo.
    echo ERROR: %COUNT% devices detected. Specify the serial:
    "%ADBEXE%" devices
    goto fail
)
set "DEV=%FIRST%"

for /f "tokens=*" %%m in ('""%ADBEXE%" -s %DEV% shell getprop ro.product.model" 2^>nul') do set "MODEL=%%m"
for /f "tokens=*" %%m in ('""%ADBEXE%" -s %DEV% shell getprop ro.build.version.release" 2^>nul') do set "ANDROID=%%m"
echo Device: %DEV%  %MODEL% (Android %ANDROID%)
echo.

echo Installing: %APK%
set "OUT=%TEMP%\quantum_install_out.txt"
"%ADBEXE%" -s %DEV% install -r "%APK%" > "%OUT%" 2>&1
type "%OUT%"
findstr /C:"Success" "%OUT%" >nul
if not errorlevel 1 goto installed

findstr /C:"INSTALL_FAILED_UPDATE_INCOMPATIBLE" "%OUT%" >nul
if errorlevel 1 goto installfailed

echo.
echo The installed %PKG% is signed with a different certificate.
echo It must be uninstalled first; local app data (login, settings) will be lost.
if "%AUTOYES%"=="1" goto forceuninstall
set /p ANS=Uninstall and continue? [y/N]:
if /i not "!ANS!"=="y" (
    echo Cancelled.
    goto fail
)

:forceuninstall
echo Uninstalling %PKG% ...
"%ADBEXE%" -s %DEV% uninstall %PKG%
echo Installing again: %APK%
"%ADBEXE%" -s %DEV% install "%APK%"
if errorlevel 1 goto installfailed

:installed
echo.
echo Package : %PKG%
"%ADBEXE%" -s %DEV% shell dumpsys package %PKG% | findstr /C:"versionName=" /C:"lastUpdateTime=" /C:"isVrApp:"

if "%DOLAUNCH%"=="1" (
    echo.
    echo Launching %PKG% ...
    "%ADBEXE%" -s %DEV% shell monkey -p %PKG% -c android.intent.category.LAUNCHER 1 >nul 2>nul
    echo Launch command sent.
)

echo.
echo Done.
goto end

:installfailed
echo.
echo ERROR: install failed. See message above.
goto fail

:find_adb
set "ADBEXE="
if defined ADB (
    if exist "%ADB%" set "ADBEXE=%ADB%"
)
if defined ADBEXE goto :eof
for /f "delims=" %%p in ('where adb 2^>nul') do (
    set "ADBEXE=%%p"
    goto :eof
)
if exist "%APPDATA%\PICO_Developer_Center_Downloads\cn\adb\platform-tools\adb.exe" set "ADBEXE=%APPDATA%\PICO_Developer_Center_Downloads\cn\adb\platform-tools\adb.exe"
if defined ADBEXE goto :eof
if exist "%APPDATA%\PICO_Developer_Center_Downloads\adb\platform-tools\adb.exe" set "ADBEXE=%APPDATA%\PICO_Developer_Center_Downloads\adb\platform-tools\adb.exe"
if defined ADBEXE goto :eof
if exist "%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe" set "ADBEXE=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
if defined ADBEXE goto :eof
if exist "%USERPROFILE%\.quantum_apk_tools\platform-tools\adb.exe" set "ADBEXE=%USERPROFILE%\.quantum_apk_tools\platform-tools\adb.exe"
goto :eof

:download_adb
echo adb not found. Downloading Android Platform-Tools...
set "TOOLS=%USERPROFILE%\.quantum_apk_tools"
if not exist "%TOOLS%" mkdir "%TOOLS%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; $u='https://dl.google.com/android/repository/platform-tools-latest-windows.zip'; $z=Join-Path $env:USERPROFILE '.quantum_apk_tools\pt.zip'; $d=Join-Path $env:USERPROFILE '.quantum_apk_tools'; try { Invoke-WebRequest -Uri $u -OutFile $z -UseBasicParsing } catch { exit 1 }; Expand-Archive -Path $z -DestinationPath $d -Force; Remove-Item $z -Force"
if exist "%TOOLS%\platform-tools\adb.exe" (
    set "ADBEXE=%TOOLS%\platform-tools\adb.exe"
    echo Downloaded: %ADBEXE%
)
goto :eof

:fail
echo.
pause
exit /b 1

:end
echo.
pause
exit /b 0
