import numpy as np
from faster_whisper import WhisperModel
from config import MODEL_SIZE, DEVICE, COMPUTE_TYPE, LANGUAGE


class Transcriber:
    def __init__(self, on_load: callable | None = None):
        if on_load:
            on_load(f"Loading model '{MODEL_SIZE}' on {DEVICE}…")
        self._model = WhisperModel(
            MODEL_SIZE,
            device=DEVICE,
            compute_type=COMPUTE_TYPE,
        )
        if on_load:
            on_load("Model ready")

    def transcribe(self, audio: np.ndarray) -> str:
        if audio.size == 0:
            return ""
        segments, _ = self._model.transcribe(
            audio,
            language=LANGUAGE,
            vad_filter=True,           # skip silence
            vad_parameters={"min_silence_duration_ms": 500},
        )
        return " ".join(s.text.strip() for s in segments).strip()
