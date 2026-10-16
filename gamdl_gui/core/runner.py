"""Background worker that runs ``gamdl`` and streams its output.

Runs in a :class:`QThread` and communicates with the UI exclusively through
Qt signals, so the GUI thread never blocks and never touches the process
directly.

Progress handling is the big change over the old tkinter version: gamdl prints
its progress with ``tqdm`` which refreshes with a carriage return (``\\r``) and
writes to *stderr*.  Reading with ``readline()`` (which only splits on ``\\n``)
smeared several refreshes into one line and produced garbage percentages.  Here
we split on both ``\\r`` and ``\\n`` so each refresh is processed individually.
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import Optional

from PySide6.QtCore import QThread, Signal


class DownloadWorker(QThread):
    lineReady = Signal(str)          # one log line (may contain ANSI codes)
    progressChanged = Signal(float)  # fraction 0.0 .. 1.0
    itemNameChanged = Signal(str)    # "now downloading" label
    finishedCode = Signal(int)       # process exit code
    launchFailed = Signal(str)       # could not start the process

    _PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
    _NAME_PATTERNS = (
        re.compile(r"Downloading\s+['\"]([^'\"]+)['\"]", re.IGNORECASE),
        re.compile(r"Destination:\s*(.+)", re.IGNORECASE),
        re.compile(r"Task Start:\s*(.+)", re.IGNORECASE),
        re.compile(r"Saving to:\s*(.+)", re.IGNORECASE),
    )

    def __init__(self, cmd: list[str], cwd: Optional[str] = None, parent=None) -> None:
        super().__init__(parent)
        self._cmd = cmd
        self._cwd = cwd
        self._proc: Optional[subprocess.Popen] = None
        self._stop_requested = False
        self._current_name = ""

    # -- control --------------------------------------------------------
    def stop(self) -> None:
        """Terminate the running process (called from the GUI thread)."""
        self._stop_requested = True
        proc = self._proc
        if proc is not None and proc.poll() is None:
            try:
                proc.kill()
            except Exception:
                pass

    @property
    def was_stopped(self) -> bool:
        return self._stop_requested

    # -- thread body ----------------------------------------------------
    def run(self) -> None:  # noqa: D401 (Qt entry point)
        env = os.environ.copy()
        env["FORCE_COLOR"] = "1"
        env["CLICOLOR_FORCE"] = "1"
        env["PYTHONUNBUFFERED"] = "1"

        try:
            self._proc = subprocess.Popen(
                self._cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                env=env,
                cwd=self._cwd,
                bufsize=0,
                **self._process_flags(),
            )
        except FileNotFoundError:
            self.launchFailed.emit("not_found")
            self.finishedCode.emit(127)
            return
        except Exception as exc:  # pragma: no cover - defensive
            self.launchFailed.emit(str(exc))
            self.finishedCode.emit(-1)
            return

        assert self._proc.stdout is not None
        stream = self._proc.stdout
        buffer = b""

        while True:
            try:
                chunk = stream.read(4096)
            except Exception:
                break
            if not chunk:
                break
            buffer += chunk
            while True:
                positions = [i for i in (buffer.find(b"\r"), buffer.find(b"\n")) if i != -1]
                if not positions:
                    break
                cut = min(positions)
                segment, buffer = buffer[:cut], buffer[cut + 1:]
                text = segment.decode("utf-8", errors="replace")
                if text.strip():
                    self._handle_line(text)

        if buffer.strip():
            self._handle_line(buffer.decode("utf-8", errors="replace"))

        try:
            stream.close()
        except Exception:
            pass

        code = self._proc.wait()
        self.finishedCode.emit(code)

    # -- helpers --------------------------------------------------------
    @staticmethod
    def _process_flags() -> dict:
        # On Windows stop the (console) gamdl child from flashing a new window
        # when launched from the windowed GUI executable.
        if os.name == "nt":
            return {"creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)}
        return {}

    def _handle_line(self, text: str) -> None:
        self.lineReady.emit(text)

        match = None
        for match in self._PERCENT_RE.finditer(text):
            pass  # keep the last percentage on the line
        if match is not None:
            try:
                self.progressChanged.emit(float(match.group(1)) / 100.0)
            except ValueError:
                pass

        name = self._extract_name(text)
        if name and name != self._current_name:
            self._current_name = name
            self.itemNameChanged.emit(name)

    def _extract_name(self, line: str) -> Optional[str]:
        for pattern in self._NAME_PATTERNS:
            match = pattern.search(line)
            if match:
                return os.path.basename(match.group(1).strip())
        return None
