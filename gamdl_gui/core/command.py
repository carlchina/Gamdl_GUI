"""Translate a :class:`Settings` object into a ``gamdl`` command line.

Keeping this in one pure function means it can be unit-tested without a GUI
and the UI layer never has to know the individual CLI flags.
"""

from __future__ import annotations

from .settings import Settings

SONG_MARKERS = ("/song/", "/album/", "/playlist/", "/station/", "/artist/")
VIDEO_MARKERS = ("/music-video/", "/post/")


def classify_urls(urls: list[str]) -> tuple[bool, bool]:
    """Return ``(has_song, has_video)`` for a batch of URLs."""
    has_song = any(marker in url for url in urls for marker in SONG_MARKERS)
    has_video = any(marker in url for url in urls for marker in VIDEO_MARKERS)
    if not has_song and not has_video:
        # Unknown link shape -> enable both, the same "just in case" behaviour
        # the original GUI used.
        has_song = has_video = True
    return has_song, has_video


def _append_path(cmd: list[str], flag: str, value: str) -> None:
    if value:
        cmd.extend([flag, value])


def build_command(
    settings: Settings, urls: list[str], program: list[str] | None = None
) -> list[str]:
    """Build the full ``gamdl`` argv list for *urls*.

    *program* is the argv prefix that launches gamdl (see
    :func:`gamdl_gui.core.gamdl.resolve_program`); it defaults to ``gamdl``.
    """
    s = settings
    cmd: list[str] = list(program) if program else ["gamdl"]

    # --- connection / locations ---------------------------------------
    _append_path(cmd, "-c", s.cookies_path)
    _append_path(cmd, "-o", s.output_path)
    _append_path(cmd, "--temp-path", s.temp_path)
    _append_path(cmd, "--log-file", s.log_file)

    # --- logging -------------------------------------------------------
    cmd.extend(["--log-level", s.log_level])
    cmd.extend(["--download-mode", s.download_mode])

    # --- behaviour -----------------------------------------------------
    if s.overwrite:
        cmd.append("--overwrite")
    if s.read_urls_as_txt:
        cmd.append("--read-urls-as-txt")

    # --- metadata ------------------------------------------------------
    _append_path(cmd, "-l", s.language)
    if s.use_album_date:
        cmd.append("--use-album-date")
    if s.fetch_extra_tags:
        cmd.append("--fetch-extra-tags")
    _append_path(cmd, "--artist-auto-select", s.artist_auto_select)

    # --- cover / playlist ---------------------------------------------
    if s.save_cover:
        cmd.append("--save-cover")
    if s.save_playlist:
        cmd.append("--save-playlist")
    _append_path(cmd, "--cover-format", s.cover_format)
    if s.cover_size:
        cmd.extend(["--cover-size", str(s.cover_size)])
    if s.truncate:
        cmd.extend(["--truncate", str(s.truncate)])
    _append_path(cmd, "--exclude-tags", s.exclude_tags)

    # --- songs / lyrics ------------------------------------------------
    _append_path(cmd, "--song-codec-priority", s.song_codec_priority)
    _append_path(cmd, "--synced-lyrics-format", s.synced_lyrics_format)
    if not s.synced_lyrics:
        cmd.append("--no-synced-lyrics")
    if s.synced_lyrics_only:
        cmd.append("--synced-lyrics-only")

    # --- music videos ---------------------------------------------------
    _append_path(cmd, "--music-video-codec-priority", s.mv_codec_priority)
    _append_path(cmd, "--music-video-remux-mode", s.mv_remux_mode)
    _append_path(cmd, "--music-video-remux-format", s.mv_remux_format)
    _append_path(cmd, "--music-video-resolution", s.mv_resolution)
    _append_path(cmd, "--uploaded-video-quality", s.uploaded_video_quality)

    # --- external tools -------------------------------------------------
    _append_path(cmd, "--ffmpeg-path", s.ffmpeg_path)
    _append_path(cmd, "--mp4decrypt-path", s.mp4decrypt_path)
    _append_path(cmd, "--mp4box-path", s.mp4box_path)
    _append_path(cmd, "--nm3u8dlre-path", s.nm3u8dlre_path)
    _append_path(cmd, "--wvd-path", s.wvd_path)

    # --- wrapper --------------------------------------------------------
    if s.use_wrapper:
        cmd.append("--use-wrapper")
        _append_path(cmd, "--wrapper-account-url", s.wrapper_account_url)
        _append_path(cmd, "--wrapper-decrypt-ip", s.wrapper_decrypt_ip)

    cmd.extend(urls)
    return cmd
