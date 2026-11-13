@echo off
setlocal
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY goto :nopython

%PY% "%~dp0install_quantum_apk.py" %*
set "RC=%ERRORLEVEL%"
echo.
pause
exit /b %RC%

:nopython
echo Python 3 not found.
echo Install Python 3.6+ from https://www.python.org/downloads/
echo and tick "Add python.exe to PATH" during setup.
echo.
echo Or install manually: adb install -r "%~dp0Quantum.apk"
echo.
pause
exit /b 1
