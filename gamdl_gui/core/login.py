"""Qt-side wrapper around the standalone webview sign-in helper.

The helper (``gamdl_gui.services.webview_login``) must run in its own process,
so this module just spawns it and reports the result back to the UI through a
Qt signal.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QThread, Signal

WEBVIEW_FLAG = "--webview-login"


def login_available() -> bool:
    """True when the webview sign-in can be offered in this environment.

    Uses a real import rather than ``importlib.util.find_spec`` because
    ``find_spec`` is not reliable for modules bundled by PyInstaller.  Importing
    ``webview`` only pulls in cheap pure-Python modules (no GUI is started).
    """
    if sys.platform not in ("darwin", "win32", "linux"):
        return False
    try:
        import webview  # noqa: F401
    except Exception:
        return False
    return True


def _login_command(output_path: str) -> list[str]:
    if getattr(sys, "frozen", False):
        # Frozen build: re-enter our own executable in "login helper" mode.
        return [sys.executable, WEBVIEW_FLAG, output_path]
    return [sys.executable, "-m", "gamdl_gui.services.webview_login", output_path]


def _process_flags() -> dict:
    # Keep the (console) helper from flashing a window on Windows; it does not
    # affect the GUI window pywebview itself opens.
    if os.name == "nt":
        return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
    return {}


class LoginWorker(QThread):
    finishedResult = Signal(bool, str)  # (ok, message)

    def __init__(self, output_path: str | Path, parent=None) -> None:
        super().__init__(parent)
        self._output = str(output_path)
        self._proc: Optional[subprocess.Popen] = None

    def run(self) -> None:  # noqa: N802 (Qt entry point)
        try:
            self._proc = subprocess.Popen(
                _login_command(self._output),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                **_process_flags(),
            )
            code = self._proc.wait()
        except Exception as exc:  # pragma: no cover - defensive
            self.finishedResult.emit(False, str(exc))
            return
        finally:
            self._proc = None

        ok = code == 0 and Path(self._output).is_file()
        self.finishedResult.emit(ok, "" if ok else f"exit code {code}")

    def cancel(self) -> None:
        proc = self._proc
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
            except Exception:
                pass
