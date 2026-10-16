"""Main panel: URLs, output directory and the most used download options."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..services.i18n import Translator


class MainPanel(QWidget):
    advancedRequested = Signal()

    def __init__(self, tr: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tr = tr

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # -- URLs --------------------------------------------------------
        self.url_label = QLabel()
        self.url_label.setObjectName("sectionTitle")
        layout.addWidget(self.url_label)

        self.url_edit = QPlainTextEdit()
        self.url_edit.setPlaceholderText("https://music.apple.com/...")
        self.url_edit.setFixedHeight(110)
        layout.addWidget(self.url_edit)

        # -- output directory -------------------------------------------
        out_row = QHBoxLayout()
        self.out_dir_label = QLabel()
        out_row.addWidget(self.out_dir_label)
        self.out_dir_edit = QLineEdit()
        out_row.addWidget(self.out_dir_edit, 1)
        self.out_dir_button = QPushButton()
        self.out_dir_button.setFixedWidth(90)
        self.out_dir_button.clicked.connect(self._browse_output)
        out_row.addWidget(self.out_dir_button)
        layout.addLayout(out_row)

        # -- options -----------------------------------------------------
        options = QGridLayout()
        options.setHorizontalSpacing(24)
        self.save_cover = QCheckBox()
        self.save_playlist = QCheckBox()
        self.synced_lyrics = QCheckBox()
        self.synced_lyrics_only = QCheckBox()
        self.overwrite = QCheckBox()
        self.read_urls_as_txt = QCheckBox()

        options.addWidget(self.save_cover, 0, 0)
        options.addWidget(self.save_playlist, 0, 1)
        options.addWidget(self.synced_lyrics, 0, 2)
        options.addWidget(self.synced_lyrics_only, 0, 3)
        options.addWidget(self.overwrite, 1, 0)
        options.addWidget(self.read_urls_as_txt, 1, 1)
        options.setColumnStretch(4, 1)
        layout.addLayout(options)

        # -- advanced ----------------------------------------------------
        adv_row = QHBoxLayout()
        adv_row.addStretch(1)
        self.advanced_button = QPushButton()
        self.advanced_button.clicked.connect(self.advancedRequested)
        adv_row.addWidget(self.advanced_button)
        layout.addLayout(adv_row)

        layout.addStretch(1)
        self.retranslate()

    # ------------------------------------------------------------------
    def _browse_output(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, self._tr.tr("select_out_dir_title"), self.out_dir_edit.text()
        )
        if path:
            self.out_dir_edit.setText(path)

    def urls(self) -> list[str]:
        text = self.url_edit.toPlainText()
        return [line.strip() for line in text.splitlines() if line.strip()]

    def retranslate(self) -> None:
        tr = self._tr
        self.url_label.setText(tr.tr("url_label"))
        self.out_dir_label.setText(tr.tr("out_dir_label"))
        self.out_dir_button.setText(tr.tr("browse_btn"))
        self.save_cover.setText(tr.tr("save_cover_cb"))
        self.save_playlist.setText(tr.tr("save_playlist_cb"))
        self.synced_lyrics.setText(tr.tr("synced_lyrics_cb"))
        self.synced_lyrics_only.setText(tr.tr("synced_lyrics_only_cb"))
        self.overwrite.setText(tr.tr("overwrite_cb"))
        self.read_urls_as_txt.setText(tr.tr("read_urls_as_txt_cb"))
        self.advanced_button.setText(tr.tr("advanced_btn"))
