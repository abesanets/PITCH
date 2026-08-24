"""
Prepare offline models for PITCH packaging.
Copies cached HuggingFace models or downloads them directly into ./models/
"""

import os
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
GIGAAM_DIR = MODELS_DIR / "gigaam-v3-e2e-rnnt"
SILERO_DIR = MODELS_DIR / "silero"

HF_CACHE = Path.home() / ".cache" / "huggingface" / "hub"
HF_GIGAAM = HF_CACHE / "models--istupakov--gigaam-v3-onnx" / "snapshots"
HF_SILERO = HF_CACHE / "models--istupakov--silero-vad-onnx" / "snapshots"

REQUIRED_GIGAAM_FILES = [
    "config.json",
    "v3_e2e_rnnt_encoder.onnx",
    "v3_e2e_rnnt_decoder.onnx",
    "v3_e2e_rnnt_joint.onnx",
    "v3_e2e_rnnt_vocab.txt",
]

REQUIRED_SILERO_FILES = [
    "config.json",
    "silero_vad.onnx",
]


def find_latest_snapshot(snapshot_dir: Path) -> Path | None:
    if not snapshot_dir.exists():
        return None
    snapshots = [d for d in snapshot_dir.iterdir() if d.is_dir()]
    if not snapshots:
        return None
    return sorted(snapshots, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def copy_or_download_gigaam():
    GIGAAM_DIR.mkdir(parents=True, exist_ok=True)
    all_exist = all((GIGAAM_DIR / f).exists() for f in REQUIRED_GIGAAM_FILES)
    if all_exist:
        print("[Prepare Models] GigaAM v3 model files already exist in ./models/gigaam-v3-e2e-rnnt.")
        return

    snapshot = find_latest_snapshot(HF_GIGAAM)
    if snapshot and all((snapshot / f).exists() for f in REQUIRED_GIGAAM_FILES):
        print(f"[Prepare Models] Copying GigaAM v3 files from cache: {snapshot} -> {GIGAAM_DIR}")
        for fname in REQUIRED_GIGAAM_FILES:
            src = snapshot / fname
            dst = GIGAAM_DIR / fname
            if not dst.exists() or dst.stat().st_size != src.stat().st_size:
                print(f"  Copying {fname} ({src.stat().st_size / (1024*1024):.1f} MB)...")
                shutil.copy2(src, dst)
        print("[Prepare Models] GigaAM v3 files copied successfully.")
    else:
        print("[Prepare Models] Downloading GigaAM v3 from HuggingFace...")
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="istupakov/gigaam-v3-onnx",
            local_dir=str(GIGAAM_DIR),
            allow_patterns=REQUIRED_GIGAAM_FILES,
        )
        print("[Prepare Models] GigaAM v3 downloaded successfully.")


def copy_or_download_silero():
    SILERO_DIR.mkdir(parents=True, exist_ok=True)
    all_exist = all((SILERO_DIR / f).exists() for f in REQUIRED_SILERO_FILES)
    if all_exist:
        print("[Prepare Models] Silero VAD model files already exist in ./models/silero.")
        return

    snapshot = find_latest_snapshot(HF_SILERO)
    if snapshot and all((snapshot / f).exists() for f in REQUIRED_SILERO_FILES):
        print(f"[Prepare Models] Copying Silero VAD files from cache: {snapshot} -> {SILERO_DIR}")
        for fname in REQUIRED_SILERO_FILES:
            src = snapshot / fname
            dst = SILERO_DIR / fname
            if not dst.exists() or dst.stat().st_size != src.stat().st_size:
                print(f"  Copying {fname} ({src.stat().st_size / (1024*1024):.1f} MB)...")
                shutil.copy2(src, dst)
        print("[Prepare Models] Silero VAD files copied successfully.")
    else:
        print("[Prepare Models] Downloading Silero VAD from HuggingFace...")
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="istupakov/silero-vad-onnx",
            local_dir=str(SILERO_DIR),
            allow_patterns=REQUIRED_SILERO_FILES,
        )
        print("[Prepare Models] Silero VAD downloaded successfully.")


def main():
    print("[Prepare Models] Starting offline models preparation...")
    copy_or_download_gigaam()
    copy_or_download_silero()
    print("[Prepare Models] All models are ready in ./models/ directory!")


if __name__ == "__main__":
    main()
