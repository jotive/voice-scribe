# Voice Scribe

Local speech-to-text using [faster-whisper](https://github.com/SYSTRAN/faster-whisper). Hold a hotkey or button to record — transcription is copied to clipboard, shown in UI, and saved to a daily log file. Runs entirely offline.

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB) ![License](https://img.shields.io/badge/license-MIT-green)

## Features

- **Hold-to-record** — hotkey (`Ctrl+Shift+Space` default) or button in UI
- **Auto-clipboard** — transcription pasted immediately after release
- **Daily log** — all transcriptions saved to `logs/YYYY-MM-DD.txt`
- **Systray** — runs in background, window togglable
- **100% local** — no API calls, no internet required
- **Configurable model** — tiny / base / small / medium / large-v2

## Requirements

- Windows 10/11
- Python 3.11 or 3.12 (3.14 may lack ctranslate2 wheels)
- NVIDIA GPU recommended (CUDA 12.x) — CPU works but is slower

## Quick start

```bat
setup.bat   # creates venv, installs deps, runs hardware check
run.bat     # launches the app
```

## Hardware check

```bat
.venv\Scripts\activate
python check_hardware.py
```

Detects your GPU/VRAM and recommends the best model + config.

## Configuration

Copy `.env.example` to `.env` and adjust:

```env
WHISPER_MODEL=small        # tiny base small medium large-v2
WHISPER_DEVICE=cuda        # cuda | cpu
WHISPER_COMPUTE=float16    # float16 (GPU) | int8 (CPU/low VRAM)
WHISPER_LANG=              # leave empty for auto-detect, or: es en fr...
WHISPER_HOTKEY=<ctrl>+<shift>+<space>
```

## Model guide (faster-whisper int8, NVIDIA)

| Model    | VRAM    | Speed  | Accuracy |
|----------|---------|--------|----------|
| tiny     | ~0.2 GB | ★★★★★  | ★★       |
| base     | ~0.3 GB | ★★★★   | ★★★      |
| small    | ~0.6 GB | ★★★    | ★★★★     |
| medium   | ~1.5 GB | ★★     | ★★★★★    |
| large-v2 | ~2.9 GB | ★      | ★★★★★    |

## Project structure

```
voice-scribe/
├── main.py            # entry point — systray, hotkey, orchestration
├── recorder.py        # mic capture via sounddevice
├── transcriber.py     # faster-whisper wrapper
├── ui.py              # tkinter dark UI
├── config.py          # settings loaded from env vars
├── check_hardware.py  # GPU/RAM check + model recommendations
├── setup.bat          # venv + deps install
├── run.bat            # launch
└── .env.example       # config template
```

## License

MIT
