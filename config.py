import os
from pathlib import Path

BASE_DIR   = Path(__file__).parent
LOG_DIR    = BASE_DIR / "logs"

MODEL_SIZE   = os.getenv("WHISPER_MODEL",   "small")   # tiny base small medium large-v2
DEVICE       = os.getenv("WHISPER_DEVICE",  "cuda")    # cuda | cpu
COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE", "float16") # float16 (GPU) | int8 (CPU)
LANGUAGE     = os.getenv("WHISPER_LANG",    None)      # None=auto-detect, "es", "en"...
HOTKEY       = os.getenv("WHISPER_HOTKEY",  "<ctrl>+<shift>+<space>")
SAMPLE_RATE  = 16_000
