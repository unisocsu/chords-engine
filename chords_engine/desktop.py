"""נקודת הכניסה של התוכנה: מפעיל את המנוע ופותח חלון (WebView2 דרך pywebview).
אם pywebview לא זמין — פותח את Edge במצב אפליקציה, ונסגר כשהחלון נסגר."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

from . import __version__, config
from . import update

TITLE = "אקורדים"
TASKBAR_TBPF_NOPROGRESS = 0x0
TASKBAR_TBPF_INDETERMINATE = 0x1
TASKBAR_TBPF_NORMAL = 0x2
TASKBAR_TBPF_ERROR = 0x4
TASKBAR_TBPF_PAUSED = 0x8


class _TaskbarProgress:
    """Windows 7+ taskbar progress without an extra Python dependency."""
    def __init__(self):
        self._taskbar = None
        self._hwnd = None
        self._lock = threading.Lock()

    def _ensure(self):
        if self._taskbar is not None and self._hwnd:
            return True
        if os.name != "nt":
            return False
        try:
            import ctypes
            from ctypes import wintypes

            hwnd = ctypes.windll.user32.FindWindowW(None, TITLE)
            if not hwnd:
                return False

            clsid = ctypes.byref((wintypes.BYTE * 16)(
                0x44, 0xF3, 0x6D, 0x56, 0xD6, 0xFD, 0xD0, 0x11,
                0x95, 0x8A, 0x00, 0x60, 0x97, 0xC9, 0xA0, 0x90
            ))
            iid = ctypes.byref((wintypes.BYTE * 16)(
                0x91, 0xFB, 0x1A, 0xEA, 0x28, 0x9E, 0x86, 0x4B,
                0x90, 0xE9, 0x9E, 0x9F, 0x8A, 0x5E, 0xE8, 0xF8
            ))
            ole32 = ctypes.windll.ole32
            ole32.CoInitialize(None)
            ptr = ctypes.c_void_p()
            hr = ole32.CoCreateInstance(clsid, None, 1, iid, ctypes.byref(ptr))
            if hr != 0 or not ptr.value:
                return False

            # ITaskbarList3 vtable: IUnknown(3), ITaskbarList::HrInit(3),
            # then SetProgressState at slot 6 and SetProgressValue at slot 7.
            vtbl = ctypes.cast(ptr, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
            self._hr_init = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p)(vtbl[3])
            self._set_state = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, wintypes.HWND, ctypes.c_uint)(vtbl[6])
            self._set_value = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_void_p, wintypes.HWND, ctypes.c_ulonglong, ctypes.c_ulonglong)(vtbl[7])
            if self._hr_init(ptr) != 0:
                return False
            self._taskbar = ptr
            self._hwnd = hwnd
            return True
        except Exception:
            return False

    def update(self, state=TASKBAR_TBPF_NOPROGRESS, progress=0.0):
        with self._lock:
            if not self._ensure():
                return
            try:
                if state != TASKBAR_TBPF_NOPROGRESS:
                    self._set_state(self._taskbar, self._hwnd, state)
                    if state == TASKBAR_TBPF_NORMAL:
                        value = max(0, min(1000, int(float(progress) * 1000)))
                        self._set_value(self._taskbar, self._hwnd, value, 1000)
                else:
                    self._set_state(self._taskbar, self._hwnd, state)
            except Exception:
                self._taskbar = None
                self._hwnd = None


def _start_taskbar_monitor():
    """Mirror the active analysis job's real progress to the Windows taskbar."""
    if os.name != "nt":
        return
    def monitor():
        last = None
        while True:
            try:
                from .server import QUEUE
                active = next((j for j in QUEUE.jobs.values() if j.status == "running"), None)
                if active:
                    key = ("running", round(active.progress, 3))
                    if key != last:
                        _TASKBAR.update(TASKBAR_TBPF_NORMAL, active.progress)
                        last = key
                else:
                    if last is not None:
                        _TASKBAR.update(TASKBAR_TBPF_NOPROGRESS)
                        last = None
            except Exception:
                pass
            time.sleep(0.2)
    threading.Thread(target=monitor, daemon=True, name="taskbar-progress").start()


_TASKBAR = _TaskbarProgress()
AUDIO_FILTER = ("קבצי שמע ווידאו (*.mp3;*.wav;*.flac;*.m4a;*.aac;*.ogg;*.opus;*.wma;*.mp4;*.mkv;*.webm;*.avi;*.mov)",
                "כל הקבצים (*.*)")


def _ours(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=1.5) as r:
            return json.loads(r.read()).get("ok") is True
    except Exception:  # noqa: BLE001
        return False


def _free(port: int) -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def _log_to_file():
    """ב-EXE בלי קונסול: הפלט נשמר לקובץ לוג (לאבחון תקלות)."""
    if sys.stdout is None or getattr(sys, "frozen", False):
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        f = open(config.DATA_DIR / "engine.log", "a", encoding="utf-8", buffering=1)
        sys.stdout = sys.stderr = f
        print(f"\n=== {time.ctime()} v{__version__} ===")


class Api:
    """פונקציות שהממשק קורא דרך window.pywebview.api"""
    _window = None

    def pick_files(self):
        import webview
        kind = getattr(getattr(webview, "FileDialog", None), "OPEN", None) or webview.OPEN_DIALOG
        return list(self._window.create_file_dialog(kind, allow_multiple=True, file_types=AUDIO_FILTER) or [])

    def pick_folder(self):
        import webview
        kind = getattr(getattr(webview, "FileDialog", None), "FOLDER", None) or webview.FOLDER_DIALOG
        res = self._window.create_file_dialog(kind)
        return list(res or [])

    def save_file(self, name: str, content: str):
        import webview
        kind = getattr(getattr(webview, "FileDialog", None), "SAVE", None) or webview.SAVE_DIALOG
        res = self._window.create_file_dialog(kind, save_filename=name)
        if not res:
            return None
        path = res if isinstance(res, str) else res[0]
        Path(path).write_text(content, encoding="utf-8-sig")
        return path

    def open_folder(self, path: str):
        subprocess.Popen(["explorer", "/select,", path])

    def fullscreen(self):
        self._window.toggle_fullscreen()

    def update_settings(self):
        return update.settings()

    def save_update_settings(self, data):
        return update.save_settings(data or {})

    def check_for_updates(self, force=False):
        return update.check(bool(force))

    def start_update_download(self, asset, version):
        return update.start_download(asset or {}, str(version or ""))

    def update_status(self):
        return update.status()

    def cancel_update_download(self):
        return update.cancel_download()

    def install_update(self):
        result = update.install_downloaded()
        if result.get("ok"):
            def close_later():
                time.sleep(1.0)
                os._exit(0)
            threading.Thread(target=close_later, daemon=True).start()
        return result

    def open_google_search(self, query: str = ""):
        """Open Google search in a native WebView window."""
        import webview
        from urllib.parse import quote_plus
        q = str(query or "").strip()
        url = "https://www.google.com/search?q=" + quote_plus(q or "site:youtube.com שיר")
        webview.create_window("חיפוש Google", url, width=1200, height=820, min_size=(800, 600))
        return {"ok": True, "url": url}

    def keep_awake(self, on: bool):
        # ES_CONTINUOUS | ES_DISPLAY_REQUIRED | ES_SYSTEM_REQUIRED — מצב הופעה: המסך לא נכבה
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | (0x3 if on else 0))


def _edge_app(url: str) -> bool:
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles")):
        exe = Path(base or "") / "Microsoft" / "Edge" / "Application" / "msedge.exe"
        if exe.exists():
            prof = config.DATA_DIR / "edge"
            proc = subprocess.Popen([str(exe), f"--app={url}", f"--user-data-dir={prof}", "--no-first-run"])
            proc.wait()
            return True
    import webbrowser
    webbrowser.open(url)
    return False


def main():
    _log_to_file()
    port = config.DEFAULT_PORT
    if _ours(port):                      # התוכנה כבר פתוחה — חלון נוסף לאותו מנוע
        _edge_app(f"http://127.0.0.1:{port}/")
        return
    while not _free(port):
        port += 1
    from .server import serve
    threading.Thread(target=serve, args=("127.0.0.1", port), daemon=True).start()
    for _ in range(100):
        if _ours(port):
            break
        time.sleep(0.1)
    url = f"http://127.0.0.1:{port}/ui/index.html"
    _start_taskbar_monitor()
    try:
        import webview
        api = Api()
        api._window = webview.create_window(TITLE, url, js_api=api, width=1360, height=880,
                                           min_size=(900, 600), text_select=True)

        def on_drop(e):
            files = (e.get("dataTransfer") or {}).get("files") or []
            paths = [f.get("pywebviewFullPath") for f in files if f.get("pywebviewFullPath")]
            if paths:
                api._window.evaluate_js(f"window.onNativeDrop({json.dumps(paths)})")

        def on_loaded():
            try:     # גרירת קבצים עם נתיב מלא (בלי העתקה)
                from webview.dom import DOMEventHandler
                api._window.dom.document.events.drop += DOMEventHandler(on_drop, True, True)
                api._window.evaluate_js("window.__nativeDrop = true")
            except Exception as ex:  # noqa: BLE001
                print("drop handler:", ex)

        api._window.events.loaded += on_loaded
        webview.start(gui="edgechromium", private_mode=False,
                      storage_path=str(config.DATA_DIR / "webview"))
    except Exception as e:  # noqa: BLE001
        print("pywebview נכשל, עובר ל-Edge:", e)
        from .server import LAST_PING
        opened = _edge_app(url)
        if not opened:                   # דפדפן רגיל: נשארים חיים כל עוד הדף שולח ping
            while time.time() - LAST_PING[0] < 60:
                time.sleep(5)
    os._exit(0)


if __name__ == "__main__":
    main()
