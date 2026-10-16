#!/usr/bin/env python3
"""Cross-platform build driver.

Usage::

    python packaging/build.py                 # lite build (manual cookies.txt)
    python packaging/build.py --webview       # include the sign-in webview flow
    python packaging/build.py --noconfirm ... # extra args pass through to PyInstaller

Results land in ``dist/``.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str]) -> int:
    spec = ROOT / "gamdl_gui.spec"
    if not spec.exists():
        print(f"spec not found: {spec}", file=sys.stderr)
        return 1

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller is not installed. Run: pip install pyinstaller", file=sys.stderr)
        return 1

    with_webview = "--webview" in argv
    passthrough = [arg for arg in argv if arg != "--webview"]

    env = os.environ.copy()
    env["GAMDL_GUI_WEBVIEW"] = "1" if with_webview else "0"
    print(f">> webview sign-in: {'on' if with_webview else 'off (lite build)'}")

    cmd = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", *passthrough, str(spec)]
    print(">>", " ".join(cmd))
    return subprocess.call(cmd, cwd=str(ROOT), env=env)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
