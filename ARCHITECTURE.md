# PITCH Codebase Architecture & File Map

This document outlines the codebase structure and responsibilities of key components.

---

## Root Directory

* `main.py` — Application entry point. Solves single-instance locks, initializes QApplication, PitchCore, ClipboardManager, and starts VoiceAssistant.
* `config.json` — Local configuration file storing hotkeys, visualizer styles, and STT model settings.
* `requirements.txt` — Project dependencies (`PyQt6`, `onnx-asr[cpu,hub]`, `soundfile`, `sounddevice`, `numpy`, `keyboard`).
* `Pitch.spec` — PyInstaller packaging configuration (configured for onedir mode, bundles `assets/` and `models/`).
* `installer.iss` — Inno Setup script to generate single-file Windows installer (`PITCH_Setup_v1.54.exe`).
* `build.ps1` — Automated script to run PyInstaller and compile the Inno Setup installer.

---

## `core/` — Business & Processing Logic

* `core/__init__.py` — Exports version constant (`__version__ = "1.54"`) and core package symbols (`PitchCore`, `STTWorker`, `ClipboardManager`, `AudioRecorder`, `LogRedirector`).
* `core/engine.py` — `PitchCore` class managing recording state, keyboard hooks, hotkey listening, and background transcription worker execution.
* `core/stt_engine.py` — `GigaAMEngine` class wrapping `onnx-asr` model `gigaam-v3-e2e-rnnt` and Silero VAD (supporting local offline `models/` directory with automatic fallback).
* `core/stt_worker.py` — `STTWorker` QThread wrapper for asynchronous execution of STT pipelines and dynamic RTF calculation.
* `core/audio_recorder.py` — `AudioRecorder` class managing sounddevice stream recording, volume callbacks, and in-RAM float32 audio numpy buffer returns.
* `core/clipboard.py` — `ClipboardManager` managing modifier key release waits and simulated text pasting via Win32 `SendInput`.
* `core/keyboard_hook.py` — Low-level Windows keyboard hook (`WindowsKeyboardHook`) for handling `Ctrl + Win` without triggering Windows Start Menu.
* `core/history_manager.py` — Dictation record persistence in `history.json` and dynamic RTF statistics tracking.
* `core/startup.py` — Windows Startup registry shortcut registration.
* `core/log_redirector.py` — Thread-safe log writer redirecting stdout/stderr with timestamps.

---

## `ui/` — Graphical Interface & Visualizer

* `ui/app/assistant.py` — `VoiceAssistant` tray application wiring UI, tray icon, clean exit handling, and core signals.
* `ui/app/dashboard.py` — `DashboardWindow` 4-tab container (Overview, Visualizer, History, Settings) and theme coordinator.
* `ui/visualizer/widgets.py` — Visualizer overlay (`OverlayWindow`) and settings preview widget (`PreviewWidget`).
* `ui/visualizer/renderers.py` — Shared pixel-art rendering functions (`draw_wave_visualizer`, `draw_matrix_visualizer`).
* `ui/app/tabs/` — Tab builders (Overview, Visualizer settings, History list, Settings).
* `ui/app/tabs/_helpers.py` — Shared helper functions for tab UI updates (hotkey badge synchronization).

---

## `tools/` — Build & Asset Scripts

* `tools/prepare_models.py` — Prepares local `models/` folder by copying from Hugging Face cache or downloading weights.
* `tools/generate_svgs.py` — Pixel-art navbar SVG icon generator.
* `tools/generate_logo.py` — High-resolution pixel-art logo and `icon.ico` generator.

