"""Application bootstrap."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from . import __version__
from .core.settings import LANGS_DIR, Settings
from .services.i18n import Translator
from .ui.main_window import MainWindow
from .ui.theme import apply_theme


def main() -> int:
    settings = Settings.load()

    app = QApplication(sys.argv)
    app.setApplicationName("Gamdl GUI")
    app.setApplicationDisplayName("Gamdl GUI")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Carlchina")

    apply_theme(app, settings.theme)

    translator = Translator(LANGS_DIR, settings.ui_language)
    window = MainWindow(settings, translator)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
