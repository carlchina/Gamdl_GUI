"""Shared look & feel: a Fusion palette that follows the system theme."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication

DARK = {
    "window": "#1e1f22",
    "base": "#2b2d30",
    "alt_base": "#232427",
    "text": "#e6e6e6",
    "disabled": "#6b6d70",
    "highlight": "#3d7eff",
    "button": "#34363a",
    "button_text": "#e6e6e6",
    "tooltip": "#2b2d30",
}


def _dark_palette() -> QPalette:
    p = QPalette()
    c = QColor
    p.setColor(QPalette.Window, c(DARK["window"]))
    p.setColor(QPalette.WindowText, c(DARK["text"]))
    p.setColor(QPalette.Base, c(DARK["base"]))
    p.setColor(QPalette.AlternateBase, c(DARK["alt_base"]))
    p.setColor(QPalette.ToolTipBase, c(DARK["tooltip"]))
    p.setColor(QPalette.ToolTipText, c(DARK["text"]))
    p.setColor(QPalette.Text, c(DARK["text"]))
    p.setColor(QPalette.Button, c(DARK["button"]))
    p.setColor(QPalette.ButtonText, c(DARK["button_text"]))
    p.setColor(QPalette.BrightText, c("#ff5555"))
    p.setColor(QPalette.Link, c(DARK["highlight"]))
    p.setColor(QPalette.Highlight, c(DARK["highlight"]))
    p.setColor(QPalette.HighlightedText, c("#ffffff"))
    for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, role, c(DARK["disabled"]))
    return p


def apply_theme(app: QApplication, mode: str = "system") -> None:
    """Apply ``system``, ``light`` or ``dark`` appearance to *app*."""
    app.setStyle("Fusion")
    resolved = mode
    if mode == "system":
        try:
            scheme = app.styleHints().colorScheme()
            resolved = "dark" if scheme == Qt.ColorScheme.Dark else "light"
        except Exception:
            resolved = "dark"

    if resolved == "dark":
        app.setPalette(_dark_palette())
    else:
        app.setPalette(app.style().standardPalette())
