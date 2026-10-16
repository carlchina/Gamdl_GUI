"""The application window: wires the panels together and owns the worker."""

from __future__ import annotations

import os
import shlex
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QByteArray
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core.command import build_command
from ..core.gamdl import resolve_program
from ..core.login import LoginWorker, login_available
from ..core.runner import DownloadWorker
from ..core.settings import Settings
from ..services.i18n import Translator
from .advanced_dialog import AdvancedDialog
from .console import LogConsole
from .main_panel import MainPanel
from .sidebar import Sidebar
from .theme import apply_theme

GAMDL_DEFAULT_COOKIE = Path.home() / ".gamdl" / "cookies.txt"


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings, translator: Translator) -> None:
        super().__init__()
        self.settings = settings
        self.tr = translator
        self.worker: Optional[DownloadWorker] = None
        self.login_worker: Optional[LoginWorker] = None
        self._cookie_filename = Path(settings.cookies_path).name if settings.cookies_path else ""

        self.setMinimumSize(900, 640)
        self._restore_geometry()
        self._build_ui()
        self._load_settings_into_ui()
        self.tr.languageChanged.connect(self._retranslate)
        self._retranslate()

    # ------------------------------------------------------------------
    # construction
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        self.sidebar = Sidebar(self.tr)
        root.addWidget(self.sidebar)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        self.main_panel = MainPanel(self.tr)
        right_layout.addWidget(self.main_panel)

        header = QHBoxLayout()
        self.console_label = QLabel()
        self.console_label.setObjectName("sectionTitle")
        header.addWidget(self.console_label)
        header.addStretch(1)
        self.clear_button = QPushButton()
        self.clear_button.clicked.connect(self._clear_console)
        header.addWidget(self.clear_button)
        right_layout.addLayout(header)

        self.console = LogConsole()
        right_layout.addWidget(self.console, 1)

        root.addWidget(right, 1)

        # signals
        self.sidebar.cookieImportRequested.connect(self._import_cookie)
        self.sidebar.loginRequested.connect(self._start_login)
        self.sidebar.startRequested.connect(self._start_download)
        self.sidebar.stopRequested.connect(self._stop_download)
        self.sidebar.languageChanged.connect(self._change_language)
        self.sidebar.themeChanged.connect(self._change_theme)
        self.main_panel.advancedRequested.connect(self._open_advanced)

        # Webview sign-in is optional: hide the button when pywebview is absent
        # (e.g. the lite build), leaving manual cookies.txt import.
        self.sidebar.login_button.setVisible(login_available())

    def _restore_geometry(self) -> None:
        geometry = self.settings.window_geometry
        if geometry:
            try:
                self.restoreGeometry(QByteArray.fromBase64(geometry.encode("ascii")))
                return
            except Exception:
                pass
        self.resize(980, 720)

    # ------------------------------------------------------------------
    # settings <-> ui
    # ------------------------------------------------------------------
    def _load_settings_into_ui(self) -> None:
        s = self.settings
        self.sidebar.log_level_combo.setCurrentText(s.log_level)
        self.sidebar.download_mode_combo.setCurrentText(s.download_mode)

        lang_index = self.sidebar.language_combo.findData(s.ui_language)
        if lang_index >= 0:
            self.sidebar.language_combo.blockSignals(True)
            self.sidebar.language_combo.setCurrentIndex(lang_index)
            self.sidebar.language_combo.blockSignals(False)

        theme_index = self.sidebar.theme_combo.findData(s.theme)
        self.sidebar.theme_combo.blockSignals(True)
        self.sidebar.theme_combo.setCurrentIndex(max(0, theme_index))
        self.sidebar.theme_combo.blockSignals(False)

        self.main_panel.out_dir_edit.setText(s.output_path)
        self.main_panel.save_cover.setChecked(s.save_cover)
        self.main_panel.save_playlist.setChecked(s.save_playlist)
        self.main_panel.synced_lyrics.setChecked(s.synced_lyrics)
        self.main_panel.synced_lyrics_only.setChecked(s.synced_lyrics_only)
        self.main_panel.overwrite.setChecked(s.overwrite)
        self.main_panel.read_urls_as_txt.setChecked(s.read_urls_as_txt)

        if self._cookie_filename:
            self.sidebar.set_cookie_saved(self._cookie_filename)

    def _collect_settings(self) -> None:
        s = self.settings
        s.log_level = self.sidebar.log_level_combo.currentText()
        s.download_mode = self.sidebar.download_mode_combo.currentText()
        s.output_path = self.main_panel.out_dir_edit.text().strip()
        s.save_cover = self.main_panel.save_cover.isChecked()
        s.save_playlist = self.main_panel.save_playlist.isChecked()
        s.synced_lyrics = self.main_panel.synced_lyrics.isChecked()
        s.synced_lyrics_only = self.main_panel.synced_lyrics_only.isChecked()
        s.overwrite = self.main_panel.overwrite.isChecked()
        s.read_urls_as_txt = self.main_panel.read_urls_as_txt.isChecked()

    # ------------------------------------------------------------------
    # actions
    # ------------------------------------------------------------------
    def _import_cookie(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr.tr("select_cookie_title"),
            "",
            "Text (*.txt);;All files (*)",
        )
        if not path:
            return
        try:
            dest_dir = GAMDL_DEFAULT_COOKIE.parent
            dest_dir.mkdir(parents=True, exist_ok=True)
            if GAMDL_DEFAULT_COOKIE.exists():
                backup = GAMDL_DEFAULT_COOKIE.with_suffix(".txt.bak")
                shutil.copy2(GAMDL_DEFAULT_COOKIE, backup)
            shutil.copy2(path, GAMDL_DEFAULT_COOKIE)
        except Exception as exc:
            QMessageBox.critical(self, self.tr.tr("error_title"), self.tr.tr("cookie_error_msg", exc))
            return

        self.settings.cookies_path = str(GAMDL_DEFAULT_COOKIE)
        self.settings.save()
        self._cookie_filename = GAMDL_DEFAULT_COOKIE.name
        self.sidebar.set_cookie_saved(self._cookie_filename)
        self.console.append_line(self.tr.tr("cookie_saved_log", str(GAMDL_DEFAULT_COOKIE)))

    def _start_login(self) -> None:
        if self.login_worker is not None and self.login_worker.isRunning():
            return

        self.sidebar.start_button.setEnabled(False)
        self.sidebar.login_button.setEnabled(False)
        self.sidebar.set_item(self.tr.tr("login_waiting"))
        self.console.append_line(self.tr.tr("login_opening_log"))

        self.login_worker = LoginWorker(str(GAMDL_DEFAULT_COOKIE), self)
        self.login_worker.finishedResult.connect(self._on_login_finished)
        self.login_worker.start()

    def _on_login_finished(self, ok: bool, message: str) -> None:
        self.login_worker = None
        self.sidebar.start_button.setEnabled(True)
        self.sidebar.login_button.setEnabled(True)
        self.sidebar.item_label.clear()

        if ok:
            self.settings.cookies_path = str(GAMDL_DEFAULT_COOKIE)
            self.settings.save()
            self._cookie_filename = GAMDL_DEFAULT_COOKIE.name
            self.sidebar.set_cookie_saved(self._cookie_filename)
            self.console.append_line(self.tr.tr("login_success_log", str(GAMDL_DEFAULT_COOKIE)))
        else:
            self.console.append_line(self.tr.tr("login_failed_log", message or "-"))

    def _open_advanced(self) -> None:
        dialog = AdvancedDialog(self.settings, self.tr, self)
        if dialog.exec():
            self.settings.save()

    def _start_download(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            return

        urls = self.main_panel.urls()
        if not urls:
            self._error("empty_url_error_msg")
            return
        if any(not url.startswith("http") for url in urls):
            self._error("invalid_url_error_msg")
            return

        self._collect_settings()
        cookies = self.settings.cookies_path or (str(GAMDL_DEFAULT_COOKIE) if GAMDL_DEFAULT_COOKIE.exists() else "")
        if not cookies:
            self._error("missing_cookie_error_msg")
            return
        self.settings.cookies_path = cookies

        cmd = build_command(self.settings, urls, program=resolve_program(self.settings))
        self.console.append_line(self.tr.tr("executing_log", shlex.join(cmd)))

        self.worker = DownloadWorker(cmd, cwd=self._working_directory())
        self.worker.lineReady.connect(self.console.append_line)
        self.worker.progressChanged.connect(self._on_progress)
        self.worker.itemNameChanged.connect(self.sidebar.set_item)
        self.worker.launchFailed.connect(self._on_launch_failed)
        self.worker.finishedCode.connect(self._on_finished)
        self.worker.start()

        self.sidebar.set_running(True)

    def _stop_download(self) -> None:
        if self.worker is None or not self.worker.isRunning():
            return
        answer = QMessageBox.question(
            self,
            self.tr.tr("stop_dl_confirm_title"),
            self.tr.tr("stop_dl_confirm_msg"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer == QMessageBox.Yes:
            self.worker.stop()
            self.console.append_line(self.tr.tr("dl_aborted_log"))

    def _on_progress(self, fraction: float) -> None:
        self.sidebar.set_progress(fraction)

    def _on_launch_failed(self, reason: str) -> None:
        if reason == "not_found":
            self.console.append_line(self.tr.tr("cmd_not_found_log"))
        else:
            self.console.append_line(self.tr.tr("launch_error_log", reason))

    def _on_finished(self, code: int) -> None:
        stopped = self.worker.was_stopped if self.worker else False
        self.worker = None
        self.sidebar.set_running(False)
        if stopped:
            return
        if code == 0:
            self.console.append_line(self.tr.tr("success_log"))
        else:
            self.console.append_line(self.tr.tr("process_exit_log", code))

    def _clear_console(self) -> None:
        self.console.clear_log()

    def _error(self, key: str) -> None:
        QMessageBox.critical(self, self.tr.tr("error_title"), self.tr.tr(key))

    # ------------------------------------------------------------------
    # appearance / language
    # ------------------------------------------------------------------
    def _change_language(self, code: str) -> None:
        self.settings.ui_language = code
        self.settings.save()
        self.tr.set_language(code)  # triggers _retranslate

    def _change_theme(self, mode: str) -> None:
        app = QApplication.instance()
        if app is not None:
            apply_theme(app, mode)
        self.settings.theme = mode
        self.settings.save()

    def _retranslate(self) -> None:
        self.setWindowTitle(f"{self.tr.tr('app_title')}  ·  v{__version__}")
        self.sidebar.retranslate()
        self.main_panel.retranslate()
        self.console_label.setText(self.tr.tr("console_label"))
        self.clear_button.setText(self.tr.tr("clear_console_btn"))

    # ------------------------------------------------------------------
    def _working_directory(self) -> str:
        """A writable cwd for gamdl.

        gamdl defaults ``temp_path`` to the current working directory, which is
        ``/`` when a macOS ``.app`` is launched from Finder.  Use the configured
        temp path when set, otherwise the system temp directory.
        """
        if self.settings.temp_path:
            try:
                Path(self.settings.temp_path).mkdir(parents=True, exist_ok=True)
            except Exception:
                pass
            return self.settings.temp_path
        return tempfile.gettempdir()

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt name)
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)
        if self.login_worker is not None and self.login_worker.isRunning():
            self.login_worker.cancel()
            self.login_worker.wait(3000)
        self._collect_settings()
        try:
            self.settings.window_geometry = bytes(self.saveGeometry().toBase64()).decode("ascii")
        except Exception:
            pass
        self.settings.save()
        super().closeEvent(event)
