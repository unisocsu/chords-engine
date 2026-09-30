"""עדכון אוטומטי לגרסת Windows דרך GitHub Releases."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

from . import __version__, config

REPO_API = "https://api.github.com/repos/unisocsu/chords-engine-windows/releases/latest"
DEFAULTS = {"enabled": True, "interval_hours": 168, "last_check": 0}

_LOCK = threading.Lock()
_CANCEL = threading.Event()
_STATUS = {
    "state": "idle", "downloaded": False, "progress": 0.0,
    "downloaded_bytes": 0, "total_bytes": 0, "error": "",
    "version": "", "path": "",
}


def _state_path() -> Path:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    return config.DATA_DIR / "update.json"


def settings() -> dict:
    try:
        data = json.loads(_state_path().read_text(encoding="utf-8"))
        return {**DEFAULTS, **data}
    except (OSError, ValueError, TypeError):
        return dict(DEFAULTS)


def save_settings(data: dict) -> dict:
    out = {**DEFAULTS, **(data or {})}
    out["enabled"] = bool(out["enabled"])
    out["interval_hours"] = int(out["interval_hours"])
    out["last_check"] = float(out["last_check"])
    _state_path().write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def should_check() -> bool:
    s = settings()
    return bool(s["enabled"]) and (time.time() - float(s["last_check"])) >= int(s["interval_hours"]) * 3600


def _version_tuple(v: str) -> tuple:
    nums = re.findall(r"\d+", str(v or ""))
    return tuple(int(x) for x in nums[:4]) or (0,)


def _variant() -> str | None:
    # The launcher passes the edition explicitly because the embedded
    # Python executable is ChordsApp.exe, not chords-<variant>.exe.
    env_variant = os.environ.get("CHORDS_VARIANT", "").strip().lower()
    if env_variant in {"tiny", "base", "small", "medium", "nomodel"}:
        return env_variant
    name = Path(sys.executable).stem.lower()
    m = re.fullmatch(r"chords-(tiny|base|small|medium|nomodel)", name)
    return m.group(1) if m else None


def _request_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "ChordsEngine-Updater",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))


def check(force: bool = False) -> dict:
    s = settings()
    if not force and not should_check():
        return {"checked": False, "update": None, "settings": s}
    try:
        data = _request_json(REPO_API)
        latest = str(data.get("tag_name") or "").lstrip("vV")
        current = __version__
        variant = _variant()
        asset_name = f"ChordsEngine-{variant}-Installer.exe" if variant else None
        asset = next((a for a in data.get("assets", []) if a.get("name") == asset_name), None)
        save_settings({**s, "last_check": time.time()})
        return {
            "checked": True,
            "update": bool(_version_tuple(latest) > _version_tuple(current) and asset),
            "current_version": current,
            "latest_version": latest,
            "variant": variant,
            "release_url": data.get("html_url", ""),
            "asset": {
                "name": asset.get("name"), "url": asset.get("browser_download_url"),
                "size": asset.get("size", 0), "digest": asset.get("digest", ""),
            } if asset else None,
            "settings": settings(),
        }
    except Exception as e:
        return {"checked": True, "update": None, "error": str(e), "settings": settings()}


def _set_status(**kwargs):
    with _LOCK:
        _STATUS.update(kwargs)


def status() -> dict:
    with _LOCK:
        return dict(_STATUS)


def start_download(asset: dict, version: str) -> dict:
    if status()["state"] == "downloading":
        return status()
    if not asset or not asset.get("url"):
        return {"state": "error", "error": "קובץ העדכון לא נמצא."}

    _CANCEL.clear()
    filename = Path(str(asset.get("name") or f"ChordsEngine-update-{version}.exe")).name
    target_dir = config.DATA_DIR / "updates"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    tmp = target.with_suffix(target.suffix + ".download")
    expected = int(asset.get("size") or 0)
    digest = str(asset.get("digest") or "")
    _set_status(state="downloading", downloaded=False, progress=0.0,
                downloaded_bytes=0, total_bytes=expected, error="",
                version=version, path=str(target))

    def worker():
        try:
            if tmp.exists():
                tmp.unlink()
            req = urllib.request.Request(str(asset["url"]), headers={"User-Agent": "ChordsEngine-Updater"})
            done = 0
            h = hashlib.sha256()
            with urllib.request.urlopen(req, timeout=30) as response, open(tmp, "wb") as out:
                while True:
                    if _CANCEL.is_set():
                        raise InterruptedError()
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
                    h.update(chunk)
                    done += len(chunk)
                    _set_status(downloaded_bytes=done,
                                progress=(done / expected if expected else 0.0))
            if expected and done != expected:
                raise ValueError(f"גודל ההורדה שונה מהצפוי ({done} במקום {expected})")
            if digest.startswith("sha256:") and h.hexdigest().lower() != digest.split(":", 1)[1].lower():
                raise ValueError("בדיקת SHA-256 של העדכון נכשלה")
            os.replace(tmp, target)
            _set_status(state="ready", downloaded=True, progress=1.0,
                        downloaded_bytes=done, total_bytes=expected,
                        path=str(target), error="")
        except InterruptedError:
            try:
                tmp.unlink()
            except OSError:
                pass
            _set_status(state="cancelled", downloaded=False, progress=0.0, error="")
        except Exception as e:
            try:
                tmp.unlink()
            except OSError:
                pass
            _set_status(state="error", downloaded=False, error=str(e))

    threading.Thread(target=worker, name="chords-update-download", daemon=True).start()
    return status()


def cancel_download():
    _CANCEL.set()
    return status()


def install_downloaded():
    p = Path(status().get("path") or "")
    if not p.is_file():
        return {"ok": False, "error": "קובץ העדכון עדיין לא מוכן."}
    subprocess.Popen([str(p)], cwd=str(p.parent))
    return {"ok": True}
