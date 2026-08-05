# PITCH

PITCH is a local desktop voice dictation assistant for Windows. It captures audio via global low-level keyboard hotkeys, performs speech-to-text transcription in memory using GigaAM v3 e2e RNNT, and pastes transcribed text directly into active applications via Win32 API.

## Requirements

- Windows 10 or 11
- Python 3.10+

## Installation

Install dependencies via pip:

```bash
pip install -r requirements.txt
```

## Running the Application

Launch the application entry point:

```bash
python main.py
```

## Building Executable and Installer

Run the automated build script:

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

- PyInstaller compiles the application into `dist/PITCH/` (onedir mode for instantaneous startup).
- If [Inno Setup 6](https://jrsoftware.org/isdl.php) is installed, `installer.iss` automatically builds `dist/PITCH_Setup_v1.12.exe`.

## Hotkeys and Controls

- **Ctrl + Win** (Press and Hold): Start recording audio. Releasing keys transcribes audio in RAM and pastes text into active window.
- **Escape**: Cancel active recording or transcription.

## Configuration

Configuration is managed in `config.json`:

- `stt_model`: Model identifier (`gigaam-v3-e2e-rnnt`).
- `hotkey_1`: Primary activation shortcut.
- `min_recording_duration`: Minimum audio threshold in seconds.
