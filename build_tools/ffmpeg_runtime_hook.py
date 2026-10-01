"""PyInstaller runtime hook: make the bundled FFmpeg discoverable by audio libraries."""
from __future__ import annotations

import os
from pathlib import Path

try:
    import imageio_ffmpeg

    ffmpeg = Path(imageio_ffmpeg.get_ffmpeg_exe()).resolve()
    if ffmpeg.is_file():
        os.environ["IMAGEIO_FFMPEG_EXE"] = str(ffmpeg)
        os.environ["FFMPEG_BINARY"] = str(ffmpeg)
        os.environ["PATH"] = str(ffmpeg.parent) + os.pathsep + os.environ.get("PATH", "")
except Exception:
    # Audio libraries can still use a system FFmpeg if one is available.
    pass
