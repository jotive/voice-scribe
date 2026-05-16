import threading
import numpy as np
import sounddevice as sd
from config import SAMPLE_RATE


class Recorder:
    def __init__(self):
        self._frames: list[np.ndarray] = []
        self._lock   = threading.Lock()
        self._stream: sd.InputStream | None = None

    def start(self):
        self._frames.clear()
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            callback=self._cb,
        )
        self._stream.start()

    def _cb(self, indata, frames, time, status):
        with self._lock:
            self._frames.append(indata.copy())

    def stop(self) -> np.ndarray:
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._frames:
                return np.zeros(0, dtype="float32")
            return np.concatenate(self._frames, axis=0).flatten()
