@echo off
chcp 65001 > nul
echo ========================================
echo   TwitchTTS Windows Exe Builder
echo ========================================
echo.

echo [1/3] Checking and installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt pyinstaller

echo.
echo [2/3] Building standalone TwitchTTS.exe...
pyinstaller --clean TwitchTTS.spec

echo.
if exist "dist\TwitchTTS.exe" (
    echo ========================================
    echo   BUILD SUCCESSFUL!
    echo   Location: dist\TwitchTTS.exe
    echo ========================================
) else (
    echo [ERROR] Build failed. Please check the error messages above.
)

pause
