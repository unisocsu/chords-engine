"""בונה EXE יחיד: release/Chords.exe
  1. PyInstaller (onedir) — המנוע + הממשק + PyTorch
  2. מוסיף whisper.cpp ומודל העברית (q5_0)
  3. אורז ל-ZIP ומצמיד למשגר קטן ב-C# (csc של .NET Framework, קיים בכל Windows)
הרצה:  python build_tools/build_exe.py
"""
from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
DIST = BUILD / "dist" / "ChordsApp"
OUT = ROOT / "release" / "Chords.exe"
SITE = Path(sys.prefix)
CSC = Path(r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe")
ICON = ROOT / "build" / "icon.ico"
WHISPER_FILES = ["whisper-cli.exe", "whisper.dll", "ggml.dll", "ggml-base.dll"]
MODEL = os.environ.get("CHORDS_MODEL", "ggml-medium-q5_0.bin")
BUNDLE_MODEL = os.environ.get("CHORDS_BUNDLE_MODEL", "1") == "1"
EXCLUDES = ["matplotlib", "IPython", "jupyter", "notebook", "pytest", "tensorflow", "torchvision", "torchaudio",
            "faster_whisper", "whisper", "ctranslate2", "tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6",
            "pandas", "demucs", "gradio", "transformers", "numba.np.ufunc.tbbpool"]


def step(msg):
    print(f"\n=== {msg}", flush=True)


def pyinstaller():
    step("PyInstaller")
    sep = ";"
    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--windowed", "--onedir",
           "--name", "ChordsApp", "--distpath", str(BUILD / "dist"), "--workpath", str(BUILD / "work"),
           "--specpath", str(BUILD),
           "--add-data", f"{ROOT / 'chords_engine' / 'ui'}{sep}chords_engine/ui",
           "--add-data", f"{SITE / 'share' / 'lv-chordia' / 'cache_data'}{sep}share/lv-chordia/cache_data",
           "--collect-all", "lv_chordia", "--collect-submodules", "librosa", "--collect-data", "librosa",
           "--collect-all", "webview", "--collect-all", "yt_dlp", "--collect-all", "imageio_ffmpeg", "--runtime-hook", str(ROOT / "build_tools" / "ffmpeg_runtime_hook.py"),\n           "--hidden-import", "clr", "--hidden-import", "soundfile",
           "--collect-binaries", "av", "--collect-submodules", "av"]
    if ICON.exists():
        cmd += ["--icon", str(ICON)]
    for e in EXCLUDES:
        cmd += ["--exclude-module", e]
    cmd.append(str(ROOT / "chords_app.py"))
    subprocess.run(cmd, check=True, cwd=ROOT)


def vendor():
    step("whisper.cpp + model")
    src = ROOT / "vendor"
    wdst = DIST / "vendor" / "whisper" / "Release"
    wdst.mkdir(parents=True, exist_ok=True)
    rel = src / "whisper" / "Release"
    for f in WHISPER_FILES + [p.name for p in rel.glob("ggml-cpu-*.dll")]:
        shutil.copy2(rel / f, wdst / f)
    mdst = DIST / "vendor" / "models"
    if BUNDLE_MODEL:
        mdst.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / "models" / MODEL, mdst / MODEL)
    elif mdst.exists():
        # Update builds intentionally contain no Whisper model.
        shutil.rmtree(mdst)


def pack() -> Path:
    step("ZIP")
    z = BUILD / "payload.zip"
    with zipfile.ZipFile(z, "w", allowZip64=True) as zf:
        for p in sorted(DIST.rglob("*")):
            if p.is_file():
                # המודל ו-DLL-ים גדולים כמעט לא נדחסים — שומרים בלי דחיסה (פריסה מהירה יותר)
                comp = zipfile.ZIP_STORED if p.suffix == ".bin" else zipfile.ZIP_DEFLATED
                zf.write(p, p.relative_to(DIST).as_posix(), compress_type=comp, compresslevel=6)
    return z


def launcher(payload: Path):
    step("launcher")
    exe = BUILD / "launcher.exe"
    csc_cmd = [str(CSC), "/nologo", "/target:winexe", "/optimize+", f"/out:{exe}",
                    "/r:System.IO.Compression.dll", "/r:System.IO.Compression.FileSystem.dll",
                    "/r:System.Windows.Forms.dll", "/r:System.Drawing.dll"]
    if ICON.exists():
        csc_cmd.append(f"/win32icon:{ICON}")
    csc_cmd.append(str(ROOT / "build_tools" / "launcher.cs"))
    subprocess.run(csc_cmd, check=True)
    from chords_engine import __version__
    ver = f"{__version__}-{time.strftime('%Y%m%d%H%M%S')}".encode("ascii")[:24].ljust(24, b"\0")
    OUT.parent.mkdir(exist_ok=True)
    with open(OUT, "wb") as out:
        out.write(exe.read_bytes())
        off = out.tell()
        with open(payload, "rb") as f:
            shutil.copyfileobj(f, out, 1 << 22)
        length = out.tell() - off
        out.write(struct.pack("<qq", off, length) + ver + b"CHRDPAK1")
    print(f"{OUT}  {OUT.stat().st_size / 1e6:.0f}MB")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    if "--skip-pyi" not in sys.argv:
        pyinstaller()
    vendor()
    launcher(pack())
