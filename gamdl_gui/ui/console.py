"""Read-only log console that renders ANSI colours as rich text."""

from __future__ import annotations

from PySide6.QtGui import QFontDatabase, QTextCursor
from PySide6.QtWidgets import QTextEdit, QWidget

from ..services.ansi import ansi_to_html


class LogConsole(QTextEdit):
    # Keep the console bounded so a long batch download cannot eat all RAM.
    MAX_BLOCKS = 5000

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setAcceptRichText(True)
        self.setUndoRedoEnabled(False)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.document().setMaximumBlockCount(self.MAX_BLOCKS)

        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPointSize(11)
        self.setFont(font)

    def append_line(self, text: str) -> None:
        bar = self.verticalScrollBar()
        follow = bar.value() >= bar.maximum() - 4
        self.append(ansi_to_html(text))
        if follow:
            bar.setValue(bar.maximum())

    def append_plain(self, text: str) -> None:
        self.append_line(text)

    def clear_log(self) -> None:
        self.clear()
