"""Left-hand control sidebar: cookies, run options and the start/stop buttons."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..services.i18n import Translator

# Display name -> UI language code
LANGUAGE_NAMES = {"en": "English", "zh": "中文"}
THEME_NAMES = {"system": "System", "light": "Light", "dark": "Dark"}


class Sidebar(QFrame):
    startRequested = Signal()
    stopRequested = Signal()
    cookieImportRequested = Signal()
    loginRequested = Signal()
    languageChanged = Signal(str)
    themeChanged = Signal(str)

    def __init__(self, tr: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._tr = tr
        self._cookie_filename = ""
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedWidth(250)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self.logo = QLabel()
        self.logo.setObjectName("logo")
        self.logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo)

        # -- cookies -----------------------------------------------------
        self.cookie_label = QLabel()
        layout.addWidget(self.cookie_label)
        self.cookie_button = QPushButton()
        self.cookie_button.clicked.connect(self.cookieImportRequested)
        layout.addWidget(self.cookie_button)

        self.login_button = QPushButton()
        self.login_button.clicked.connect(self.loginRequested)
        layout.addWidget(self.login_button)

        # -- log level ---------------------------------------------------
        self.log_level_label = QLabel()
        layout.addWidget(self.log_level_label)
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        layout.addWidget(self.log_level_combo)

        # -- download mode ----------------------------------------------
        self.download_mode_label = QLabel()
        layout.addWidget(self.download_mode_label)
        self.download_mode_combo = QComboBox()
        self.download_mode_combo.addItems(["ytdlp", "nm3u8dlre"])
        layout.addWidget(self.download_mode_combo)

        # -- ui language -------------------------------------------------
        self.language_label = QLabel()
        layout.addWidget(self.language_label)
        self.language_combo = QComboBox()
        for code, name in LANGUAGE_NAMES.items():
            self.language_combo.addItem(name, code)
        self.language_combo.currentIndexChanged.connect(self._emit_language)
        layout.addWidget(self.language_combo)

        # -- theme -------------------------------------------------------
        self.theme_label = QLabel()
        layout.addWidget(self.theme_label)
        self.theme_combo = QComboBox()
        for code, name in THEME_NAMES.items():
            self.theme_combo.addItem(name, code)
        self.theme_combo.currentIndexChanged.connect(self._emit_theme)
        layout.addWidget(self.theme_combo)

        layout.addStretch(1)

        # -- progress ----------------------------------------------------
        self.item_label = QLabel()
        self.item_label.setWordWrap(True)
        self.item_label.setStyleSheet("color: palette(mid);")
        layout.addWidget(self.item_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 1000)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        layout.addWidget(self.progress)

        # -- actions -----------------------------------------------------
        self.start_button = QPushButton()
        self.start_button.setMinimumHeight(42)
        self.start_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.start_button.clicked.connect(self.startRequested)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton()
        self.stop_button.setMinimumHeight(36)
        self.stop_button.clicked.connect(self.stopRequested)
        layout.addWidget(self.stop_button)

        self.version_label = QLabel()
        self.version_label.setStyleSheet("color: palette(mid);")
        self.version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.version_label)

        self.set_running(False)
        self.retranslate()

    # ------------------------------------------------------------------
    def _emit_language(self) -> None:
        code = self.language_combo.currentData()
        if code:
            self.languageChanged.emit(code)

    def _emit_theme(self) -> None:
        code = self.theme_combo.currentData()
        if code:
            self.themeChanged.emit(code)

    def set_cookie_saved(self, filename: str) -> None:
        self._cookie_filename = filename
        self.retranslate()

    def set_running(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.stop_button.setVisible(running)
        self.progress.setVisible(running)
        if not running:
            self.progress.setValue(0)
            self.item_label.clear()
        else:
            self.progress.setRange(0, 0)  # indeterminate until we see a %

    def set_progress(self, fraction: float) -> None:
        self.progress.setRange(0, 1000)
        self.progress.setValue(int(max(0.0, min(1.0, fraction)) * 1000))

    def set_item(self, name: str) -> None:
        metrics = self.item_label.fontMetrics()
        elided = metrics.elidedText(name, Qt.ElideMiddle, self.width() - 40)
        self.item_label.setText(elided)
        self.item_label.setToolTip(name)

    def retranslate(self) -> None:
        tr = self._tr
        self.logo.setText(tr.tr("logo_text"))
        self.cookie_label.setText(tr.tr("cookie_label"))
        if self._cookie_filename:
            self.cookie_button.setText(tr.tr("cookie_saved_btn_text", self._cookie_filename))
        else:
            self.cookie_button.setText(tr.tr("cookie_btn"))
        self.login_button.setText(tr.tr("login_btn"))
        self.log_level_label.setText(tr.tr("log_level_label"))
        self.download_mode_label.setText(tr.tr("dl_mode_label"))
        self.language_label.setText(tr.tr("language_label"))
        self.theme_label.setText(tr.tr("theme_label"))
        self.start_button.setText(tr.tr("start_download_btn"))
        self.stop_button.setText(tr.tr("stop_dl_btn"))
        self.version_label.setText(tr.tr("version_label"))
