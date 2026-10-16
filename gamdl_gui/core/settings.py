"""Persistent application settings.

Every option the GUI exposes is stored on a single ``Settings`` dataclass and
serialised to ``config.json`` next to the project root.  This replaces the
dozens of loose ``StringVar`` objects of the old tkinter version and finally
makes the output directory, log level, checkboxes, ... survive a restart.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any

UI_LANGUAGES = ("en", "zh")

IS_FROZEN = bool(getattr(sys, "frozen", False))


def resource_dir() -> Path:
    """Directory holding bundled, read-only resources (``langs/``)."""
    if IS_FROZEN:
        # PyInstaller: sys._MEIPASS is set for onefile/onedir and .app bundles.
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    # ``gamdl_gui/core/settings.py`` -> project root is three levels up.
    return Path(__file__).resolve().parent.parent.parent


def user_config_dir() -> Path:
    """Writable per-user config directory (used only when frozen)."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "Gamdl GUI"


APP_DIR = resource_dir()
LANGS_DIR = APP_DIR / "langs"
# In dev keep the historic ``config.json`` in the repo; when packaged the app
# bundle is read-only, so persist to the user's config directory instead.
CONFIG_PATH = (user_config_dir() / "config.json") if IS_FROZEN else (APP_DIR / "config.json")


def default_output_path() -> str:
    return str(Path.home() / "Downloads" / "Apple Music")


@dataclass
class Settings:
    # --- interface -----------------------------------------------------
    ui_language: str = "en"
    theme: str = "system"  # system | light | dark
    window_geometry: str = ""

    # --- general -------------------------------------------------------
    cookies_path: str = ""
    output_path: str = field(default_factory=default_output_path)
    temp_path: str = ""
    log_level: str = "INFO"
    log_file: str = ""
    download_mode: str = "ytdlp"
    overwrite: bool = False
    read_urls_as_txt: bool = False

    # --- metadata ------------------------------------------------------
    # ``language`` is gamdl's *metadata* language (-l), not the UI language.
    language: str = "en-US"
    use_album_date: bool = False
    artist_auto_select: str = ""  # empty == gamdl default
    date_tag_template: str = ""
    no_exceptions: bool = False

    # --- songs ---------------------------------------------------------
    save_cover: bool = True
    save_playlist: bool = False
    cover_format: str = "jpg"
    cover_size: int = 1200
    truncate: int = 0  # 0 == unset
    song_codec_priority: str = "aac-web"
    exclude_tags: str = ""
    synced_lyrics: bool = True
    synced_lyrics_format: str = "lrc"
    synced_lyrics_only: bool = False

    # --- music videos --------------------------------------------------
    mv_codec_priority: str = "h264,h265"
    mv_remux_format: str = "m4v"
    mv_resolution: str = "1080p"
    uploaded_video_quality: str = "best"

    # --- naming templates (gamdl 3.x; empty == gamdl default) ----------
    album_folder_template: str = ""
    compilation_folder_template: str = ""
    no_album_folder_template: str = ""
    playlist_folder_template: str = ""
    single_disc_file_template: str = ""
    multi_disc_file_template: str = ""
    no_album_file_template: str = ""
    playlist_file_template: str = ""

    # --- DRM (gamdl 3.x) ------------------------------------------------
    drm_backend: str = "widevine"
    wvd_path: str = ""
    prd_path: str = ""

    # --- external tools / wrapper -------------------------------------
    gamdl_path: str = ""  # empty == auto-detect (bundled / PATH)
    ffmpeg_path: str = ""
    nm3u8dlre_path: str = ""
    database_path: str = ""
    use_wrapper: bool = False
    wrapper_url: str = ""
    wrapper_decrypt_host: str = ""
    wrapper_decrypt_port: str = ""

    # ------------------------------------------------------------------
    @classmethod
    def load(cls, path: Path | str = CONFIG_PATH) -> "Settings":
        path = Path(path)
        data: dict[str, Any] = {}
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}

        # Backwards compatibility with the old tkinter config which only
        # stored ``{"language": "zh"}`` and meant the *UI* language.
        if "ui_language" not in data and "language" in data:
            legacy = data.pop("language")
            if legacy in UI_LANGUAGES:
                data["ui_language"] = legacy
            else:
                # Not a known UI code -> probably already a metadata language.
                data["language"] = legacy

        # gamdl 3.x renamed/removed a few of the options the GUI used to store.
        # Migrate the old keys so an existing config.json keeps working.
        if "wrapper_account_url" in data and "wrapper_url" not in data:
            data["wrapper_url"] = data.pop("wrapper_account_url")
        else:
            data.pop("wrapper_account_url", None)
        decrypt_ip = data.pop("wrapper_decrypt_ip", None)
        if decrypt_ip and "wrapper_decrypt_host" not in data:
            host, _, port = str(decrypt_ip).partition(":")
            data["wrapper_decrypt_host"] = host
            if port:
                data["wrapper_decrypt_port"] = port

        # gamdl 3.x renamed the legacy AAC codecs (``aac-legacy`` -> ``aac-web``).
        codec = data.get("song_codec_priority")
        if isinstance(codec, str) and codec.endswith("-legacy"):
            data["song_codec_priority"] = codec[: -len("-legacy")] + "-web"

        known = {f.name for f in fields(cls)}
        data = {k: v for k, v in data.items() if k in known}
        return cls(**data)

    def save(self, path: Path | str = CONFIG_PATH) -> None:
        path = Path(path)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(
                json.dumps(asdict(self), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            os.replace(tmp, path)
        except Exception:
            # Never let a config write crash the app.
            pass
