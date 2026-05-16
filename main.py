import sys
import threading
import pyperclip
import pystray
from PIL import Image, ImageDraw
from pynput import keyboard
from datetime import datetime
from pathlib import Path

from config import HOTKEY, LOG_DIR, MODEL_SIZE
from recorder import Recorder
from transcriber import Transcriber
from model_manager import ensure_model
from ui import App


# ── State ─────────────────────────────────────────────────────────────────────
_recorder    : Recorder
_transcriber : Transcriber
_app         : App
_hotkey_active = False


def _make_icon() -> Image.Image:
    img = Image.new("RGB", (64, 64), "#1e1e1e")
    d   = ImageDraw.Draw(img)
    d.ellipse([16, 16, 48, 48], fill="#007acc")
    d.ellipse([26, 26, 38, 38], fill="white")
    return img


# ── Record / Transcribe ───────────────────────────────────────────────────────

def start_recording():
    _recorder.start()
    _app.set_status("● recording", "#f44336")
    _app.set_recording(True)


def stop_recording():
    _app.set_recording(False)
    _app.set_status("◌ transcribing…", "#ffb74d")

    def _run():
        audio = _recorder.stop()
        text  = _transcriber.transcribe(audio)

        if text:
            pyperclip.copy(text)
            _save_log(text)
            _app.after(0, lambda: _app.append(text, "text"))
            _app.after(0, lambda: _app.set_status("✓ copied to clipboard", "#4caf50"))
        else:
            _app.after(0, lambda: _app.append("[no speech detected]", "warn"))
            _app.after(0, lambda: _app.set_status("● idle", "#666666"))

    threading.Thread(target=_run, daemon=True).start()


def _save_log(text: str):
    LOG_DIR.mkdir(exist_ok=True)
    ts   = datetime.now()
    path = LOG_DIR / f"{ts.strftime('%Y-%m-%d')}.txt"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"[{ts.strftime('%H:%M:%S')}] {text}\n")


# ── Hotkey ────────────────────────────────────────────────────────────────────

def _build_hotkey_listener():
    global _hotkey_active

    # parse hotkey string like "<ctrl>+<shift>+<space>"
    parts  = HOTKEY.split("+")
    combo  = frozenset(
        keyboard.Key[p.strip("<>")]
        if p.startswith("<") else keyboard.KeyCode.from_char(p)
        for p in parts
    )
    pressed: set = set()

    def on_press(key):
        global _hotkey_active
        pressed.add(key)
        if combo <= pressed and not _hotkey_active:
            _hotkey_active = True
            start_recording()

    def on_release(key):
        global _hotkey_active
        pressed.discard(key)
        if _hotkey_active and not (combo <= pressed):
            _hotkey_active = False
            stop_recording()

    return keyboard.Listener(on_press=on_press, on_release=on_release)


# ── Systray ───────────────────────────────────────────────────────────────────

def _build_tray():
    def show(_):  _app.after(0, _app.show)
    def quit_(_): _app.after(0, _app.destroy); tray.stop()

    tray = pystray.Icon(
        "voice-scribe",
        _make_icon(),
        "Voice Scribe",
        menu=pystray.Menu(
            pystray.MenuItem("Show", show, default=True),
            pystray.MenuItem("Quit", quit_),
        ),
    )
    return tray


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    global _recorder, _transcriber, _app

    _recorder = Recorder()
    _app      = App(on_record_start=start_recording, on_record_stop=stop_recording)
    _app.set_hotkey_label(HOTKEY)

    # load model in background so UI appears immediately
    def _load():
        global _transcriber
        ok = ensure_model(
            MODEL_SIZE,
            on_status=lambda msg, color: _app.after(0, lambda: _app.set_status(msg, color)),
        )
        if not ok:
            return
        _transcriber = Transcriber(on_load=lambda msg: _app.after(0, lambda: _app.append(msg, "info")))
        _app.after(0, lambda: _app.set_status("● idle", "#666666"))

    threading.Thread(target=_load, daemon=True).start()

    # hotkey listener
    listener = _build_hotkey_listener()
    listener.start()

    # systray in background thread
    tray = _build_tray()
    threading.Thread(target=tray.run, daemon=True).start()

    _app.mainloop()
    listener.stop()


if __name__ == "__main__":
    main()
