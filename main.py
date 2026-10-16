#!/usr/bin/env python3
"""Entry point: ``python main.py`` (or ``python -m gamdl_gui``).

Also acts as a "multi-call" binary for packaged builds: when invoked with
``--webview-login <path>`` it runs the standalone webview sign-in helper
instead of the GUI (pywebview needs the process main thread, so it cannot run
inside the Qt app).
"""

import sys

WEBVIEW_FLAG = "--webview-login"


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == WEBVIEW_FLAG:
        from gamdl_gui.services.webview_login import main as login_main

        return login_main([sys.argv[2]])

    from gamdl_gui.app import main as gui_main

    return gui_main()


if __name__ == "__main__":
    raise SystemExit(main())
