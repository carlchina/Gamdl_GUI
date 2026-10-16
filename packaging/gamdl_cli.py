#!/usr/bin/env python3
"""Entry point for the *bundled* ``gamdl`` console executable.

The GUI launches this binary as a child process (see
``gamdl_gui/core/gamdl.py``) so that a packaged app is fully self-contained and
does not require the user to ``pip install gamdl``.
"""

from __future__ import annotations

import multiprocessing

from gamdl.cli.cli import main

if __name__ == "__main__":
    # gamdl 3.x downloads through yt-dlp inside a ``multiprocessing`` worker.  In
    # a frozen (PyInstaller) build the *spawn* start method re-executes this very
    # binary as ``gamdl --multiprocessing-fork ...``; PyInstaller's bundled
    # ``pyi_rth_multiprocessing`` runtime hook only intercepts that call if
    # ``freeze_support()`` is invoked here.  Without it the worker's arguments
    # reach the click CLI and abort with
    # ``Error: No such option: --multiprocessing-fork``.
    multiprocessing.freeze_support()
    main()
