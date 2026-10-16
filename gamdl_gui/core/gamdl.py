"""Locate the ``gamdl`` executable to run.

Resolution order:

1. an explicit path set by the user (Advanced settings),
2. a ``gamdl`` binary bundled next to the frozen app (see ``gamdl_gui.spec``),
3. ``gamdl`` found on ``PATH``,
4. the bare name ``gamdl`` (lets the OS give a clear "not found" error).
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from .settings import Settings


def _names() -> list[str]:
    return ["gamdl.exe", "gamdl"] if os.name == "nt" else ["gamdl"]


def _bundled_candidates() -> list[Path]:
    if not getattr(sys, "frozen", False):
        return []
    dirs = [
        Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent)),
        Path(sys.executable).parent,
    ]
    return [directory / name for directory in dirs for name in _names()]


def resolve_program(settings: Settings) -> list[str]:
    """Return the argv prefix that launches gamdl."""
    if settings.gamdl_path:
        return [settings.gamdl_path]
    for candidate in _bundled_candidates():
        if candidate.is_file():
            return [str(candidate)]
    found = shutil.which("gamdl")
    if found:
        return [found]
    return ["gamdl"]


def describe(settings: Settings) -> str:
    """Human readable description of the resolved gamdl, for the log."""
    return resolve_program(settings)[0]
