"""Prepare whisper.cpp and the selected Whisper GGML model for the Windows build."""
from __future__ import annotations

import io
import os
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"
WHISPER_TAG = "b5130"
WHISPER_ZIP = f"https://github.com/ggml-org/whisper.cpp/releases/download/{WHISPER_TAG}/whisper-bin-x64.zip"

MODEL_NAME = os.environ.get("CHORDS_MODEL", "ggml-medium-q5_0.bin")
MODEL_URL = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{MODEL_NAME}"
MODEL = VENDOR / "models" / MODEL_NAME
CLI = VENDOR / "whisper" / "Release" / "whisper-cli.exe"


def fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def main() -> None:
    if not CLI.exists():
        print("Downloading whisper.cpp", WHISPER_TAG)
        data = fetch(WHISPER_ZIP)
        if not data.startswith(b"PK"):
            sys.exit("whisper.cpp download is not a ZIP file")
        (VENDOR / "whisper").mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(io.BytesIO(data)).extractall(VENDOR / "whisper")

    MODEL.parent.mkdir(parents=True, exist_ok=True)
    if not MODEL.exists() or MODEL.stat().st_size < 10_000_000:
        print(f"Downloading Whisper model: {MODEL_NAME}")
        subprocess.run(
            ["curl", "-L", "--fail", "--retry", "3", "-C", "-", "-o", str(MODEL), MODEL_URL],
            check=True,
        )

    if MODEL.stat().st_size < 10_000_000 or MODEL.read_bytes()[:4] != b"lmgg":
        sys.exit(f"Invalid or incomplete Whisper model: {MODEL_NAME}")

    print(f"Whisper model ready: {MODEL_NAME} ({MODEL.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
