"""
Checks GPU/CPU/RAM and recommends which Whisper models you can run.
Usage: python check_hardware.py
"""
import subprocess
import sys

# faster-whisper VRAM requirements (int8 quantization, approximate)
MODELS = [
    ("tiny",     0.2,  "~0.15 GB",  "fastest, lower accuracy"),
    ("base",     0.5,  "~0.3 GB",   "good for quick notes"),
    ("small",    1.2,  "~0.6 GB",   "recommended balance"),
    ("medium",   2.5,  "~1.5 GB",   "high accuracy"),
    ("large-v2", 4.0,  "~2.9 GB",   "best accuracy, slow on weak GPU"),
    ("large-v3", 4.5,  "~3.1 GB",   "latest, marginally better than v2"),
]

GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


def get_gpu():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.total,memory.free",
             "--format=csv,noheader,nounits"],
            text=True, stderr=subprocess.DEVNULL,
        )
        gpus = []
        for line in out.strip().splitlines():
            name, total, free = [x.strip() for x in line.split(",")]
            gpus.append({"name": name, "total_mb": int(total), "free_mb": int(free)})
        return gpus
    except Exception:
        return []


def get_ram_gb():
    try:
        out = subprocess.check_output(
            ["powershell", "-Command",
             "(Get-CimInstance Win32_PhysicalMemory | Measure-Object Capacity -Sum).Sum / 1GB"],
            text=True, stderr=subprocess.DEVNULL,
        )
        return float(out.strip())
    except Exception:
        return 0.0


def check_cuda():
    try:
        import torch
        return torch.cuda.is_available(), torch.version.cuda
    except ImportError:
        return False, None


def main():
    print(f"\n{BOLD}{'='*55}")
    print("  WHISPER HARDWARE CHECK")
    print(f"{'='*55}{RESET}\n")

    # ── Python ────────────────────────────────────────────────────────────────
    print(f"  Python : {sys.version.split()[0]}")

    # ── RAM ───────────────────────────────────────────────────────────────────
    ram = get_ram_gb()
    print(f"  RAM    : {ram:.0f} GB")

    # ── GPU ───────────────────────────────────────────────────────────────────
    gpus = get_gpu()
    cuda_ok, cuda_ver = check_cuda()

    if gpus:
        for g in gpus:
            total_gb = g["total_mb"] / 1024
            free_gb  = g["free_mb"]  / 1024
            print(f"  GPU    : {g['name']}")
            print(f"  VRAM   : {total_gb:.1f} GB total  /  {free_gb:.1f} GB free")
        cuda_str = f"CUDA {cuda_ver}" if cuda_ok else f"{YELLOW}NOT detected (install torch+cuda){RESET}"
        print(f"  CUDA   : {cuda_str}")
    else:
        print(f"  GPU    : {YELLOW}No NVIDIA GPU detected — will use CPU{RESET}")

    print()

    # ── Model recommendations ─────────────────────────────────────────────────
    print(f"{BOLD}  Model recommendations (faster-whisper int8):{RESET}")
    print(f"  {'Model':<12} {'VRAM':<10} {'Status':<10} Notes")
    print(f"  {'-'*52}")

    vram_gb = gpus[0]["total_mb"] / 1024 if gpus else 0.0
    device  = "GPU" if gpus else "CPU"

    for name, req, size, notes in MODELS:
        if gpus:
            fits = vram_gb >= req
            if fits:
                status = f"{GREEN}✓ fits{RESET}"
            elif vram_gb >= req * 0.75:
                status = f"{YELLOW}⚠ tight{RESET}"
            else:
                status = f"{RED}✗ skip{RESET}"
        else:
            # CPU: anything runs, just slow; large models very slow
            fits = req <= 2.5
            status = f"{GREEN}✓ ok{RESET}" if fits else f"{YELLOW}⚠ slow{RESET}"

        print(f"  {name:<12} {size:<10} {status:<20} {notes}")

    # ── Recommendation ────────────────────────────────────────────────────────
    print()
    if gpus:
        rec = "large-v2" if vram_gb >= 4.0 else "medium" if vram_gb >= 2.5 else "small"
        dev = "cuda"
        ctype = "float16"
    else:
        rec  = "small"
        dev  = "cpu"
        ctype = "int8"

    print(f"  {BOLD}Recommended config for .env:{RESET}")
    print(f"  {CYAN}WHISPER_MODEL={rec}")
    print(f"  WHISPER_DEVICE={dev}")
    print(f"  WHISPER_COMPUTE={ctype}{RESET}")
    print()


if __name__ == "__main__":
    main()
