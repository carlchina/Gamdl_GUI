#!/usr/bin/env python3
"""Entry point for the *bundled* ``gamdl`` console executable.

The GUI launches this binary as a child process (see
``gamdl_gui/core/gamdl.py``) so that a packaged app is fully self-contained and
does not require the user to ``pip install gamdl``.
"""

from gamdl.cli.cli import main

if __name__ == "__main__":
    main()
