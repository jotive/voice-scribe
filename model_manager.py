import sys
from pathlib import Path
from tkinter import messagebox
import tkinter as tk

MODEL_SIZES = {
    "tiny":     "~150 MB",
    "base":     "~290 MB",
    "small":    "~970 MB",
    "medium":   "~1.5 GB",
    "large-v2": "~3.1 GB",
    "large-v3": "~3.1 GB",
}

HF_CACHE = Path.home() / ".cache" / "huggingface" / "hub"


def is_cached(model_size: str) -> bool:
    name = f"models--Systran--faster-whisper-{model_size}"
    candidate = HF_CACHE / name
    return candidate.exists() and any(candidate.rglob("*.bin"))


def confirm_download(model_size: str) -> bool:
    size = MODEL_SIZES.get(model_size, "unknown size")
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    answer = messagebox.askyesno(
        "Download model",
        f"Model '{model_size}' ({size}) is not cached locally.\n\n"
        f"Download from Hugging Face now?\n"
        f"(saved to ~/.cache/huggingface/hub — one-time download)",
        parent=root,
    )
    root.destroy()
    return answer


def ensure_model(model_size: str, on_status=None) -> bool:
    """Returns False if user declined download."""
    if is_cached(model_size):
        return True
    if not confirm_download(model_size):
        if on_status:
            on_status("⚠ model download cancelled — choose a cached model in .env", "#ffb74d")
        return False
    return True
