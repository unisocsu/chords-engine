"""YouTube download support through yt-dlp.

The downloader intentionally uses yt-dlp's Python API so the packaged EXE does not
depend on a separate Python installation or a yt-dlp.exe file.
"""
from __future__ import annotations

import threading
import uuid
from pathlib import Path

from . import config

DOWNLOAD_DIR = config.DATA_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

_LOCK = threading.RLock()
_JOBS: dict[str, dict] = {}


def _job_public(job: dict) -> dict:
    return {
        "id": job["id"],
        "status": job["status"],
        "progress": round(float(job.get("progress", 0)), 4),
        "downloaded_bytes": int(job.get("downloaded_bytes", 0)),
        "total_bytes": int(job.get("total_bytes", 0)),
        "speed": job.get("speed"),
        "eta": job.get("eta"),
        "filename": job.get("filename", ""),
        "song_id": job.get("song_id"),
        "error": job.get("error"),
    }


def status(job_id: str) -> dict | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        return _job_public(job) if job else None


def _progress(job_id: str, d: dict) -> None:
    with _LOCK:
        job = _JOBS.get(job_id)
        if not job:
            return
        job["status"] = d.get("status", job["status"])
        job["downloaded_bytes"] = d.get("downloaded_bytes", 0) or 0
        job["total_bytes"] = d.get("total_bytes", 0) or d.get("total_bytes_estimate", 0) or 0
        job["speed"] = d.get("speed")
        job["eta"] = d.get("eta")
        job["filename"] = d.get("filename") or job.get("filename", "")
        if job["total_bytes"]:
            job["progress"] = min(1.0, job["downloaded_bytes"] / job["total_bytes"])
        if d.get("status") == "finished":
            job["progress"] = 1.0


def _run(job_id: str, url: str, options: dict) -> None:
    try:
        # NetFree and other HTTPS filtering/proxy setups can install their root CA
        # in the Windows certificate store instead of Python's bundled certifi store.
        # truststore makes Python's SSL stack use that system store while keeping
        # certificate verification enabled.
        try:
            import truststore
            truststore.inject_into_ssl()
        except ImportError:
            pass
        import yt_dlp

        title = (options.get("title") or "").strip()
        outtmpl = str(DOWNLOAD_DIR / "%(title).180s [%(id)s].%(ext)s")
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": outtmpl,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "windowsfilenames": True,
            "progress_hooks": [lambda d: _progress(job_id, d)],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = Path(ydl.prepare_filename(info))
            if not path.exists():
                # Some post-processors can change the final extension.
                stem = path.stem
                candidates = sorted(DOWNLOAD_DIR.glob(stem + ".*"), key=lambda p: p.stat().st_mtime, reverse=True)
                if candidates:
                    path = candidates[0]
            if not path.exists():
                raise FileNotFoundError("yt-dlp סיים את ההורדה אבל הקובץ לא נמצא")

        with _LOCK:
            job = _JOBS[job_id]
            job["status"] = "downloaded"
            job["progress"] = 1.0
            job["filename"] = str(path)
            job["title"] = title or info.get("title") or path.stem

        # ניתוח אוטומטי לאחר שההורדה הסתיימה.
        from .server import _submit
        analyze_options = dict(options.get("analysis_options") or {})
        analyze_job = _submit(str(path), analyze_options)
        with _LOCK:
            _JOBS[job_id]["status"] = "analyzing"
            _JOBS[job_id]["analysis_job_id"] = analyze_job.id
            _JOBS[job_id]["song_id"] = analyze_job.song_id
            _JOBS[job_id]["analysis"] = analyze_job.public()
    except Exception as exc:  # noqa: BLE001
        with _LOCK:
            if job_id in _JOBS:
                _JOBS[job_id]["status"] = "error"
                _JOBS[job_id]["error"] = str(exc)


def start(url: str, analysis_options: dict | None = None) -> dict:
    url = (url or "").strip()
    if not url:
        raise ValueError("לא הוזן קישור YouTube")
    if not (url.startswith("https://") or url.startswith("http://")):
        raise ValueError("הקישור חייב להתחיל ב-http:// או https://")

    job_id = uuid.uuid4().hex[:12]
    job = {
        "id": job_id,
        "status": "queued",
        "progress": 0.0,
        "downloaded_bytes": 0,
        "total_bytes": 0,
        "speed": None,
        "eta": None,
        "filename": "",
        "song_id": None,
        "error": None,
    }
    with _LOCK:
        _JOBS[job_id] = job
    threading.Thread(target=_run, args=(job_id, url, {"analysis_options": analysis_options or {}}),
                     daemon=True, name="yt-dlp-download").start()
    return _job_public(job)


def enrich_status(job_id: str) -> dict | None:
    with _LOCK:
        job = _JOBS.get(job_id)
        if not job:
            return None
        analysis_id = job.get("analysis_job_id")
    if analysis_id:
        from .server import QUEUE
        aj = QUEUE.jobs.get(analysis_id)
        if aj:
            with _LOCK:
                job["analysis"] = aj.public()
                job["song_id"] = aj.song_id
                if aj.status == "done":
                    job["status"] = "done"
                elif aj.status in ("error", "cancelled"):
                    job["status"] = aj.status
                    job["error"] = aj.error
    return status(job_id)
