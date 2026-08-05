# PITCH Codebase Architecture & File Map

This document outlines the codebase structure and responsibilities of key components.

---

## 📂 Root Directory

* `main.py` — Application entry point. Solves single-instance locks, initializes QApplication, PitchCore, ClipboardManager, and starts VoiceAssistant.
* `config.json` — Local configuration file storing hotkeys, visualizer styles, and STT model settings.
* `corrections.json` — Custom vocabulary replacement map.
* `requirements.txt` — Project dependencies (`PyQt6`, `onnx-asr[cpu,hub]`, `soundfile`, `sounddevice`, `numpy`, `rapidfuzz`, `keyboard`, `pyperclip`).

---

## 📂 `core/` — Business & Processing Logic

* `core/__init__.py` — Exports core package symbols (`PitchCore`, `STTWorker`, `ClipboardManager`, `AudioRecorder`, `LogRedirector`).
* `core/engine.py` — `PitchCore` class managing recording state, keyboard hooks, hotkeys listening, and background transcription worker execution.
* `core/stt_engine.py` — `GigaAMEngine` class wrapping `onnx-asr` model `gigaam-v3-e2e-rnnt` and Silero VAD.
* `core/stt_worker.py` — `STTWorker` QThread wrapper for asynchronous execution of STT pipelines.
* `core/postprocessor.py` — `TermPostprocessor` handling fuzzy vocabulary replacements via `rapidfuzz`.
* `core/audio_recorder.py` — `AudioRecorder` class managing sounddevice stream recording and volume callbacks.
* `core/clipboard.py` — `ClipboardManager` managing modifier key release waits and simulated text pasting via Win32 `SendInput`.
* `core/keyboard_hook.py` — Low-level Windows keyboard hook (`WindowsKeyboardHook`) for handling `Ctrl + Win` without triggering Windows Start Menu.
* `core/history_manager.py` — Dictation record persistence in `history.json`.
* `core/startup.py` — Windows Startup registry shortcut registration.

---

## 📂 `ui/` — Graphical Interface & Visualizer

* `ui/app/assistant.py` — `VoiceAssistant` tray application wiring UI, tray icon, and core signals.
* `ui/app/dashboard.py` — `DashboardWindow` tab container and theme coordinator.
* `ui/visualizer/widgets.py` — High-quality antialiased Qt visualizer overlay (`OverlayWindow`).
* `ui/app/tabs/` — Tab builders (Overview, Visualizer settings, History list, Settings, Recognition options).
