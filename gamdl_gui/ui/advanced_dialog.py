"""Modal dialog exposing the more advanced gamdl options.

These are the flags gamdl gained over time that the original GUI never
surfaced: ALAC/lossless codec priority, metadata language, cover/playlist
options, lyrics formats, music-video settings, the wrapper decryptor and the
external tool paths.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..core.settings import Settings
from ..services.i18n import Translator

SONG_CODECS = [
    "aac-legacy",
    "aac-he-legacy",
    "aac",
    "aac-he",
    "aac-binaural",
    "aac-downmix",
    "aac-he-binaural",
    "aac-he-downmix",
    "atmos",
    "ac3",
    "alac",
    "ask",
]
LYRICS_FORMATS = ["lrc", "srt", "ttml"]
COVER_FORMATS = ["jpg", "png", "raw"]
MV_CODECS = ["h264,h265", "h265,h264", "h264", "h265", "ask"]
REMUX_MODES = ["ffmpeg", "mp4box"]
REMUX_FORMATS = ["m4v", "mp4"]
RESOLUTIONS = ["240p", "360p", "480p", "540p", "720p", "1080p", "1440p", "2160p"]
UPLOADED_QUALITIES = ["best", "ask"]
ARTIST_SELECTS = [
    "",
    "main-albums",
    "compilation-albums",
    "live-albums",
    "singles-eps",
    "all-albums",
    "top-songs",
    "music-videos",
]
METADATA_LANGUAGES = ["en-US", "en-GB", "zh-CN", "ja-JP", "ko-KR", "de-DE", "fr-FR", "es-ES"]


class AdvancedDialog(QDialog):
    def __init__(self, settings: Settings, tr: Translator, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._s = settings
        self._tr = tr
        self.setWindowTitle(tr.tr("advanced_title"))
        self.resize(680, 760)

        outer = QVBoxLayout(self)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        scroll.setWidget(content)
        outer.addWidget(scroll)

        layout = QVBoxLayout(content)
        layout.setSpacing(14)

        self._build_metadata(layout)
        self._build_cover(layout)
        self._build_song(layout)
        self._build_video(layout)
        self._build_paths(layout)
        self._build_wrapper(layout)
        layout.addStretch(1)

        buttons = QDialogButtonBox()
        ok = buttons.addButton(tr.tr("ok_btn"), QDialogButtonBox.AcceptRole)
        cancel = buttons.addButton(tr.tr("cancel_btn"), QDialogButtonBox.RejectRole)
        reset = buttons.addButton(tr.tr("reset_btn"), QDialogButtonBox.ResetRole)
        ok.clicked.connect(self._on_accept)
        cancel.clicked.connect(self.reject)
        reset.clicked.connect(self._on_reset)
        outer.addWidget(buttons)

    # ------------------------------------------------------------------
    def _group(self, title_key: str, parent_layout: QVBoxLayout) -> QFormLayout:
        box = QGroupBox(self._tr.tr(title_key))
        form = QFormLayout(box)
        form.setLabelAlignment(Qt.AlignRight)
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        parent_layout.addWidget(box)
        return form

    @staticmethod
    def _combo(values: list[str], current: str, editable: bool = False) -> QComboBox:
        combo = QComboBox()
        combo.addItems(values)
        if editable:
            combo.setEditable(True)
        if current and current not in values:
            combo.addItem(current)
        idx = combo.findText(current)
        combo.setCurrentIndex(idx if idx >= 0 else 0)
        return combo

    def _path_row(self, line: QLineEdit, directory: bool, title_key: str) -> QWidget:
        row = QWidget()
        h = QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(line, 1)
        btn = QPushButton(self._tr.tr("browse_btn"))
        btn.setFixedWidth(80)
        btn.clicked.connect(lambda: self._browse(line, directory, title_key))
        h.addWidget(btn)
        return row

    def _browse(self, line: QLineEdit, directory: bool, title_key: str) -> None:
        if directory:
            path = QFileDialog.getExistingDirectory(self, self._tr.tr(title_key), line.text())
        else:
            path, _ = QFileDialog.getOpenFileName(self, self._tr.tr(title_key), line.text())
        if path:
            line.setText(path)

    # -- sections -------------------------------------------------------
    def _build_metadata(self, layout: QVBoxLayout) -> None:
        form = self._group("group_metadata", layout)
        self.lang = self._combo(METADATA_LANGUAGES, self._s.language, editable=True)
        form.addRow(self._tr.tr("metadata_language_label"), self.lang)

        self.artist_auto = self._combo(ARTIST_SELECTS, self._s.artist_auto_select)
        form.addRow(self._tr.tr("artist_auto_select_label"), self.artist_auto)

        self.use_album_date = QCheckBox(self._tr.tr("use_album_date_cb"))
        self.use_album_date.setChecked(self._s.use_album_date)
        form.addRow("", self.use_album_date)

        self.fetch_extra_tags = QCheckBox(self._tr.tr("fetch_extra_tags_cb"))
        self.fetch_extra_tags.setChecked(self._s.fetch_extra_tags)
        form.addRow("", self.fetch_extra_tags)

    def _build_cover(self, layout: QVBoxLayout) -> None:
        form = self._group("group_cover", layout)
        self.cover_format = self._combo(COVER_FORMATS, self._s.cover_format)
        form.addRow(self._tr.tr("cover_format_label"), self.cover_format)

        self.cover_size = QSpinBox()
        self.cover_size.setRange(0, 10000)
        self.cover_size.setValue(self._s.cover_size)
        form.addRow(self._tr.tr("cover_size_label"), self.cover_size)

        self.truncate = QSpinBox()
        self.truncate.setRange(0, 500)
        self.truncate.setSpecialValueText(self._tr.tr("unset"))
        self.truncate.setValue(self._s.truncate)
        form.addRow(self._tr.tr("truncate_label"), self.truncate)

        self.exclude_tags = QLineEdit(self._s.exclude_tags)
        self.exclude_tags.setPlaceholderText("comment,lyrics,copyright")
        form.addRow(self._tr.tr("exclude_tags_label"), self.exclude_tags)

    def _build_song(self, layout: QVBoxLayout) -> None:
        form = self._group("group_song", layout)
        self.song_codec = self._combo(SONG_CODECS, self._s.song_codec_priority)
        form.addRow(self._tr.tr("song_codec_label"), self.song_codec)

        self.lyrics_format = self._combo(LYRICS_FORMATS, self._s.synced_lyrics_format)
        form.addRow(self._tr.tr("synced_lyrics_format_label"), self.lyrics_format)

        self.lyrics_only = QCheckBox(self._tr.tr("synced_lyrics_only_cb"))
        self.lyrics_only.setChecked(self._s.synced_lyrics_only)
        form.addRow("", self.lyrics_only)

    def _build_video(self, layout: QVBoxLayout) -> None:
        form = self._group("group_video", layout)
        self.mv_codec = self._combo(MV_CODECS, self._s.mv_codec_priority)
        form.addRow(self._tr.tr("mv_codec_label"), self.mv_codec)

        self.mv_resolution = self._combo(RESOLUTIONS, self._s.mv_resolution)
        form.addRow(self._tr.tr("mv_resolution_label"), self.mv_resolution)

        self.mv_remux_mode = self._combo(REMUX_MODES, self._s.mv_remux_mode)
        form.addRow(self._tr.tr("mv_remux_mode_label"), self.mv_remux_mode)

        self.mv_remux_format = self._combo(REMUX_FORMATS, self._s.mv_remux_format)
        form.addRow(self._tr.tr("mv_remux_format_label"), self.mv_remux_format)

        self.uploaded_quality = self._combo(UPLOADED_QUALITIES, self._s.uploaded_video_quality)
        form.addRow(self._tr.tr("uploaded_quality_label"), self.uploaded_quality)

    def _build_paths(self, layout: QVBoxLayout) -> None:
        form = self._group("group_paths", layout)

        self.gamdl_path = QLineEdit(self._s.gamdl_path)
        self.gamdl_path.setPlaceholderText("gamdl")
        form.addRow(self._tr.tr("gamdl_path_label"), self._path_row(self.gamdl_path, False, "select_file_title"))

        self.temp_path = QLineEdit(self._s.temp_path)
        form.addRow(self._tr.tr("temp_path_label"), self._path_row(self.temp_path, True, "select_dir_title"))

        self.log_file = QLineEdit(self._s.log_file)
        form.addRow(self._tr.tr("log_file_label"), self._path_row(self.log_file, False, "select_file_title"))

        self.wvd_path = QLineEdit(self._s.wvd_path)
        form.addRow(self._tr.tr("wvd_path_label"), self._path_row(self.wvd_path, True, "select_dir_title"))

        self.ffmpeg_path = QLineEdit(self._s.ffmpeg_path)
        self.ffmpeg_path.setPlaceholderText("ffmpeg")
        form.addRow(self._tr.tr("ffmpeg_path_label"), self.ffmpeg_path)

        self.mp4decrypt_path = QLineEdit(self._s.mp4decrypt_path)
        self.mp4decrypt_path.setPlaceholderText("mp4decrypt")
        form.addRow(self._tr.tr("mp4decrypt_path_label"), self.mp4decrypt_path)

        self.mp4box_path = QLineEdit(self._s.mp4box_path)
        self.mp4box_path.setPlaceholderText("MP4Box")
        form.addRow(self._tr.tr("mp4box_path_label"), self.mp4box_path)

        self.nm3u8dlre_path = QLineEdit(self._s.nm3u8dlre_path)
        self.nm3u8dlre_path.setPlaceholderText("N_m3u8DL-RE")
        form.addRow(self._tr.tr("nm3u8dlre_path_label"), self.nm3u8dlre_path)

    def _build_wrapper(self, layout: QVBoxLayout) -> None:
        form = self._group("group_wrapper", layout)
        self.use_wrapper = QCheckBox(self._tr.tr("use_wrapper_cb"))
        self.use_wrapper.setChecked(self._s.use_wrapper)
        form.addRow("", self.use_wrapper)

        self.wrapper_account_url = QLineEdit(self._s.wrapper_account_url)
        self.wrapper_account_url.setPlaceholderText("http://127.0.0.1:30020/")
        form.addRow(self._tr.tr("wrapper_account_url_label"), self.wrapper_account_url)

        self.wrapper_decrypt_ip = QLineEdit(self._s.wrapper_decrypt_ip)
        self.wrapper_decrypt_ip.setPlaceholderText("127.0.0.1:10020")
        form.addRow(self._tr.tr("wrapper_decrypt_ip_label"), self.wrapper_decrypt_ip)

    # -- actions --------------------------------------------------------
    def _on_accept(self) -> None:
        s = self._s
        s.language = self.lang.currentText().strip() or "en-US"
        s.artist_auto_select = self.artist_auto.currentText().strip()
        s.use_album_date = self.use_album_date.isChecked()
        s.fetch_extra_tags = self.fetch_extra_tags.isChecked()

        s.cover_format = self.cover_format.currentText()
        s.cover_size = self.cover_size.value()
        s.truncate = self.truncate.value()
        s.exclude_tags = self.exclude_tags.text().strip()

        s.song_codec_priority = self.song_codec.currentText()
        s.synced_lyrics_format = self.lyrics_format.currentText()
        s.synced_lyrics_only = self.lyrics_only.isChecked()

        s.mv_codec_priority = self.mv_codec.currentText()
        s.mv_resolution = self.mv_resolution.currentText()
        s.mv_remux_mode = self.mv_remux_mode.currentText()
        s.mv_remux_format = self.mv_remux_format.currentText()
        s.uploaded_video_quality = self.uploaded_quality.currentText()

        s.temp_path = self.temp_path.text().strip()
        s.log_file = self.log_file.text().strip()
        s.gamdl_path = self.gamdl_path.text().strip()
        s.wvd_path = self.wvd_path.text().strip()
        s.ffmpeg_path = self.ffmpeg_path.text().strip()
        s.mp4decrypt_path = self.mp4decrypt_path.text().strip()
        s.mp4box_path = self.mp4box_path.text().strip()
        s.nm3u8dlre_path = self.nm3u8dlre_path.text().strip()

        s.use_wrapper = self.use_wrapper.isChecked()
        s.wrapper_account_url = self.wrapper_account_url.text().strip()
        s.wrapper_decrypt_ip = self.wrapper_decrypt_ip.text().strip()
        self.accept()

    def _on_reset(self) -> None:
        defaults = Settings()
        self.lang.setCurrentText(defaults.language)
        self.artist_auto.setCurrentText(defaults.artist_auto_select)
        self.use_album_date.setChecked(defaults.use_album_date)
        self.fetch_extra_tags.setChecked(defaults.fetch_extra_tags)
        self.cover_format.setCurrentText(defaults.cover_format)
        self.cover_size.setValue(defaults.cover_size)
        self.truncate.setValue(defaults.truncate)
        self.exclude_tags.setText(defaults.exclude_tags)
        self.song_codec.setCurrentText(defaults.song_codec_priority)
        self.lyrics_format.setCurrentText(defaults.synced_lyrics_format)
        self.lyrics_only.setChecked(defaults.synced_lyrics_only)
        self.mv_codec.setCurrentText(defaults.mv_codec_priority)
        self.mv_resolution.setCurrentText(defaults.mv_resolution)
        self.mv_remux_mode.setCurrentText(defaults.mv_remux_mode)
        self.mv_remux_format.setCurrentText(defaults.mv_remux_format)
        self.uploaded_quality.setCurrentText(defaults.uploaded_video_quality)
        self.temp_path.setText(defaults.temp_path)
        self.log_file.setText(defaults.log_file)
        self.gamdl_path.setText(defaults.gamdl_path)
        self.wvd_path.setText(defaults.wvd_path)
        self.ffmpeg_path.setText(defaults.ffmpeg_path)
        self.mp4decrypt_path.setText(defaults.mp4decrypt_path)
        self.mp4box_path.setText(defaults.mp4box_path)
        self.nm3u8dlre_path.setText(defaults.nm3u8dlre_path)
        self.use_wrapper.setChecked(defaults.use_wrapper)
        self.wrapper_account_url.setText(defaults.wrapper_account_url)
        self.wrapper_decrypt_ip.setText(defaults.wrapper_decrypt_ip)
