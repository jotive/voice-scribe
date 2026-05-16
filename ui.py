import tkinter as tk
from tkinter import font as tkfont
from datetime import datetime

# ── Colors ────────────────────────────────────────────────────────────────────
BG       = "#1e1e1e"
BG2      = "#252526"
BG3      = "#0d0d0d"
FG       = "#cccccc"
FG_DIM   = "#666666"
ACCENT   = "#007acc"
RED      = "#f44336"
GREEN    = "#4caf50"
YELLOW   = "#ffb74d"


class App(tk.Tk):
    def __init__(self, on_record_start, on_record_stop):
        super().__init__()
        self._on_start = on_record_start
        self._on_stop  = on_record_stop
        self._recording = False

        self.title("Voice Scribe")
        self.configure(bg=BG)
        self.geometry("520x560")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self.hide)

        self._build()

    def _build(self):
        mono = tkfont.Font(family="Consolas", size=9)
        ui   = tkfont.Font(family="Segoe UI",  size=9)
        ui_s = tkfont.Font(family="Segoe UI",  size=8)

        # ── header ──────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg="#181818", height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Voice Scribe", bg="#181818", fg=FG,
                 font=tkfont.Font(family="Segoe UI", size=11)).pack(side="left", padx=14, pady=8)

        self._status = tk.Label(hdr, text="● idle", bg="#181818", fg=FG_DIM, font=ui_s)
        self._status.pack(side="right", padx=14)

        tk.Frame(self, bg="#333333", height=1).pack(fill="x")

        # ── transcript area ──────────────────────────────────────────────────
        txt_frame = tk.Frame(self, bg=BG3)
        txt_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self._txt = tk.Text(
            txt_frame, bg=BG3, fg=FG, font=mono,
            relief="flat", bd=0, wrap="word",
            padx=10, pady=8,
            state="disabled",
            insertbackground=FG,
        )
        sb = tk.Scrollbar(txt_frame, command=self._txt.yview, bg=BG2, troughcolor=BG2)
        self._txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._txt.pack(fill="both", expand=True)

        # color tags
        self._txt.tag_config("ts",    foreground=FG_DIM)
        self._txt.tag_config("text",  foreground=FG)
        self._txt.tag_config("info",  foreground=ACCENT)
        self._txt.tag_config("warn",  foreground=YELLOW)

        tk.Frame(self, bg="#333333", height=1).pack(fill="x")

        # ── controls ────────────────────────────────────────────────────────
        ctrl = tk.Frame(self, bg=BG2, height=56)
        ctrl.pack(fill="x")
        ctrl.pack_propagate(False)

        self._btn = tk.Button(
            ctrl, text="⏺  Hold to Record",
            bg=ACCENT, fg="white", activebackground="#005f99", activeforeground="white",
            font=ui, relief="flat", bd=0, padx=16,
            cursor="hand2",
        )
        self._btn.pack(side="left", padx=12, pady=10, ipady=4)
        self._btn.bind("<ButtonPress-1>",   lambda _: self._press())
        self._btn.bind("<ButtonRelease-1>", lambda _: self._release())

        clr = tk.Button(
            ctrl, text="Clear",
            bg=BG2, fg=FG_DIM, activebackground="#333333", activeforeground=FG,
            font=ui_s, relief="flat", bd=0, padx=10,
            cursor="hand2", command=self._clear,
        )
        clr.pack(side="right", padx=12)

        self._hotkey_lbl = tk.Label(ctrl, text="", bg=BG2, fg=FG_DIM, font=ui_s)
        self._hotkey_lbl.pack(side="right", padx=4)

    # ── public API ────────────────────────────────────────────────────────────

    def set_hotkey_label(self, hotkey: str):
        self._hotkey_lbl.config(text=f"or {hotkey}")

    def set_status(self, text: str, color: str = FG_DIM):
        self._status.config(text=text, fg=color)

    def append(self, text: str, tag: str = "text"):
        self._txt.config(state="normal")
        if tag == "text":
            ts = datetime.now().strftime("%H:%M:%S")
            self._txt.insert("end", f"[{ts}] ", "ts")
        self._txt.insert("end", text + "\n", tag)
        self._txt.see("end")
        self._txt.config(state="disabled")

    def hide(self):
        self.withdraw()

    def show(self):
        self.deiconify()
        self.lift()

    # ── button handlers ───────────────────────────────────────────────────────

    def _press(self):
        if not self._recording:
            self._recording = True
            self._btn.config(text="⏹  Recording…", bg=RED)
            self._on_start()

    def _release(self):
        if self._recording:
            self._recording = False
            self._btn.config(text="⏺  Hold to Record", bg=ACCENT)
            self._on_stop()

    def set_recording(self, active: bool):
        """Called from hotkey thread — schedule on UI thread."""
        self.after(0, self._press if active else self._release)

    def _clear(self):
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.config(state="disabled")
