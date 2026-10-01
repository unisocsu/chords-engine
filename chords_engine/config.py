"""נתיבים והגדרות ברירת מחדל. אפשר לדרוס כל נתיב במשתנה סביבה."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


ROOT = _root()
VENDOR = Path(os.environ.get("CHORDS_VENDOR", ROOT / "vendor"))
WHISPER_CLI = Path(os.environ.get("CHORDS_WHISPER_CLI", VENDOR / "whisper" / "Release" / "whisper-cli.exe"))
DATA_DIR = Path(os.environ.get("CHORDS_DATA", Path(os.environ.get("LOCALAPPDATA", Path.home())) / "ChordsEngine"))
LIBRARY_DIR = DATA_DIR / "library"
MODELS_DIR = Path(os.environ.get("CHORDS_MODELS", VENDOR / "models"))
if not MODELS_DIR.exists() or not any(MODELS_DIR.glob("*.bin")):
    MODELS_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "ChordsEngine" / "models"
MODEL_DIRS = [MODELS_DIR, DATA_DIR / "models"]
UI_DIR = Path(__file__).resolve().parent / "ui"

UI_LANG = os.environ.get("CHORDS_UI_LANG", "en").lower()
if UI_LANG not in {"he", "en"}:
    UI_LANG = "en"

DEFAULT_WHISPER_MODEL = "ggml-medium.en-q5_0.bin" if UI_LANG == "en" else "ggml-medium-q5_0.bin"
CHORD_VOCABULARIES = {
    "submission": {"name": "רחב — Submission", "description": "אוצר אקורדים רחב לשימוש כללי"},
    "ismir2017": {"name": "בסיסי — ISMIR 2017", "description": "אוצר מצומצם יותר לניתוח יציב ופשוט"},
    "full": {"name": "מלא — Full", "description": "אוצר האקורדים המלא של lv-chordia"},
}
DEFAULT_PORT = 8765

DEFAULT_ANALYZE_OPTIONS = {
    "language": "en" if UI_LANG == "en" else "he",
    "whisper_model": DEFAULT_WHISPER_MODEL,
    "accurate_timing": False,
    "threads": max(1, os.cpu_count() or 4),
    "vad": False,
    "separate_vocals": False,
    "chord_vocabulary": "submission",
    "min_chord_duration": 0.35,
    "snap_to_beats": True,
    "prompt": "",
    "lyrics_text": "",
    "skip_lyrics": False,
    "folder": "",
}


def _model_files(pattern: str) -> list[Path]:
    out = []
    for d in MODEL_DIRS:
        if d.exists():
            out += [p for p in d.glob(pattern) if p.stat().st_size > 100_000]
    return out


def whisper_model_path(name: str) -> Path:
    p = Path(name)
    if p.is_absolute():
        return p
    for d in MODEL_DIRS:
        if (d / name).exists():
            return d / name
    others = [m for m in _model_files("ggml-*.bin") if "silero" not in m.name]
    return others[0] if others else MODELS_DIR / name


def available_models() -> list[str]:
    return sorted({p.name for p in _model_files("ggml-*.bin") if "silero" not in p.name})


def vad_model_path() -> Path | None:
    hits = sorted(_model_files("ggml-silero*.bin"))
    return hits[-1] if hits else None
