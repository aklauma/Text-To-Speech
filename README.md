# Twitch Text-To-Speech

Minimalist pixelated desktop application that reads Twitch chat messages aloud using SAPI5 voices on Windows. Features a deep black pixel aesthetic, high-contrast typography, and dynamic adaptation to the Windows system accent color.

## Features
- **Pixel UI**: Custom frameless window with interactive status indicator `( ● ) LIVE` / `( ○ ) OFFLINE` and pixel typography (`Monocraft`).
- **Dashboard (Split View)**: Settings and live chat stream visible side-by-side on a single screen.
- **Voice & Volume Controls**: Selection of Windows SAPI5 voice engines and volume slider with a one-click `[ TEST VOICE ]` preview button.
- **System Adaptation**: Automatically inherits the Windows system accent color (via DWM registry) and system language (`SYSTEM`, `RU`, `EN`).
- **Inline Navigation**: Seamlessly switch between `[ LOG ]`, `[ BLACKLIST ]`, and `[ REWARDS ]` without modal popups.
- **Blacklist Filter**: Ignore specific chat users with fast addition and removal (via button or `Delete` key).

## Built with
- Python 3
- PyQt5
- TwitchIO
- pywin32 (Windows SAPI5)

## Requirements
- Windows 10 / 11 (64-bit)
- Twitch OAuth token (`oauth:xxxxxx`) and channel name

## Run from source
```bash
pip install -r requirements.txt
python app.py
```

## Build Executable (.exe)
To package into a single standalone `.exe` using PyInstaller:

```bash
pip install pyinstaller
pyinstaller TwitchTTS.spec
```
Or simply double-click `build.bat` on Windows.
The compiled executable will be placed in the `dist/` directory: `dist/TwitchTTS.exe`.

## Settings
Settings are persisted automatically to `settings.json` next to the executable (channel, selected voice, volume, blacklist, UI language, and optionally the OAuth token).
