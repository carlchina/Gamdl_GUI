# Gamdl GUI

Gamdl GUI is a modern, user-friendly graphical interface for [gamdl](https://github.com/glomatico/gamdl) (an Apple Music Downloader). It provides an easy way to download songs, albums, playlists, and music videos from Apple Music without needing to use the command line directly.

<img width="800" height="1356" alt="image" src="https://github.com/user-attachments/assets/da27eb86-1c9d-455b-b0d8-6bdbc14422a2" />


## Features

- **Modern interface**: built with **PySide6 (Qt)** — native widgets, resizable layout and a dark/light/system theme.
- **Easy cookie management**: sign in to Apple Music in a built-in webview and the app captures the required cookie automatically — or import a `cookies.txt` manually (the previous file is backed up).
- **Batch downloading**: paste multiple Apple Music URLs (songs, albums, playlists, stations, artists, videos) and download them all at once.
- **Real-time console**: gamdl's coloured log is rendered inline, with a reliable progress bar and current-track label.
- **Full gamdl option coverage**:
  - Download mode (`ytdlp` / `nm3u8dlre`) and log level.
  - **Song codec priority** — `alac` for lossless, or the various AAC/Atmos/AC3 codecs.
  - Metadata **language**, album-release-date tagging, extra tags, artist auto-select.
  - Cover image options (format / size), M3U8 playlist export, filename truncation, tag exclusion.
  - Synced-lyrics format (`lrc`/`srt`/`ttml`) and lyrics-only mode.
  - Music-video resolution / codec / remux mode & format, post-video quality.
  - Temp directory, log file and all external tool paths (ffmpeg, mp4decrypt, MP4Box, N_m3u8DL-RE).
  - **Wrapper decryption** settings (`--use-wrapper`, account URL, decrypt IP).
- **Remembers everything**: output directory, log level, download mode, checkboxes, language, theme and window size are saved to `config.json`.
- **Multi-language UI**: English / 中文, switchable on the fly.

## Prerequisites

1. **Python 3.10** or higher (gamdl itself requires ≥ 3.10).
2. **gamdl** — the core downloader:
   ```bash
   pip install gamdl
   ```
   *Note: `gamdl` needs additional tools such as `ffmpeg` (and `mp4decrypt` / `MP4Box` / `N_m3u8DL-RE` for some modes). See the [gamdl documentation](https://github.com/glomatico/gamdl) for full setup instructions.*

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/carlchina/Gamdl_GUI.git
   cd Gamdl_GUI
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. *(Optional)* For the one-click **Sign in to Apple Music** flow:
   ```bash
   pip install -r requirements-webview.txt
   ```
   Without it the app still works — just import `cookies.txt` manually.

## Usage

```bash
python main.py
```
or, equivalently:
```bash
python -m gamdl_gui
```

### Quick start

1. **Get cookies** — either:
   - click **Sign in to Apple Music**: a native webview opens, you log in normally (2FA included) and the app captures the `media-user-token` cookie automatically; or
   - click **Import cookies.txt** and pick a file you exported from your browser.

   (Apple Music requires this — gamdl technically only needs the single `media-user-token` cookie for `.music.apple.com`.)
2. **Paste URLs**: enter your Apple Music URLs in the box (one per line).
3. **Select output directory**.
4. **Configure options**: download mode, checkboxes, and **Advanced Settings…** for codecs, lyrics, videos, wrapper, tool paths, etc.
5. **Start Download 🎉** and watch the log console. Use **Stop Download** to abort.

## Project structure

```
Gamdl_GUI/
├── main.py                     # entry point (python main.py)
├── gamdl_gui/                  # PySide6 application package
│   ├── app.py                  # QApplication bootstrap
│   ├── core/
│   │   ├── settings.py         # Settings dataclass + config.json persistence
│   │   ├── command.py          # Settings -> gamdl argv
│   │   ├── gamdl.py            # locate the gamdl executable
│   │   ├── login.py            # Qt wrapper around the webview sign-in helper
│   │   └── runner.py           # QThread worker streaming gamdl output
│   ├── services/
│   │   ├── ansi.py             # ANSI -> Qt rich text
│   │   ├── i18n.py             # live language switching
│   │   └── webview_login.py    # standalone Apple Music sign-in + cookie capture
│   └── ui/
│       ├── main_window.py      # window wiring
│       ├── sidebar.py          # cookies / options / start-stop
│       ├── main_panel.py       # URLs / output / common options
│       ├── advanced_dialog.py  # advanced gamdl options
│       ├── console.py          # coloured log console
│       └── theme.py            # system / light / dark palette
├── langs/{en,zh}.json          # translations
├── packaging/
│   ├── gamdl_cli.py            # entry point for the bundled gamdl executable
│   ├── build.py                # cross-platform PyInstaller driver
│   ├── make_icon.py            # regenerates icon.png / icon.icns / icon.ico
│   ├── hooks/                  # custom PyInstaller hooks (Qt plugin pruning)
│   ├── icon.png                # 1024px master icon
│   ├── icon.icns               # macOS icon
│   └── icon.ico                # Windows icon
├── gamdl_gui.spec              # PyInstaller build recipe
├── requirements.txt            # runtime deps (PySide6 …)
├── requirements-webview.txt    # optional: pywebview sign-in flow
└── legacy/gamdl_gui_ctk.py     # the original tkinter (customtkinter) version
```

## Packaging (standalone executable)

The app can be built into a self-contained bundle that needs **no Python and no
`gamdl` installation** on the target machine.  The spec produces a single
`dist/` folder (or `Gamdl GUI.app` on macOS) containing two executables that
share one set of dependencies:

- `Gamdl GUI` — the Qt interface,
- `gamdl` — the downloader engine, which the GUI invokes automatically.

```bash
pip install pyinstaller
python packaging/build.py            # lite build (manual cookies.txt)
python packaging/build.py --webview  # include the sign-in webview flow
```

`--webview` bundles `pywebview` plus its native dependencies. Without it
the sign-in button is simply hidden and manual cookie import is used, keeping
the lite bundle smaller.  Because pywebview uses the **OS** web engine
(WKWebView / WebView2 / WebKitGTK) instead of embedding Chromium, the cost is
small — on macOS it measured **≈ +9 MB (137 MB → 146 MB)**, versus roughly
+200 MB for a QtWebEngine-based approach.

On Windows the sign-in window relies on the **WebView2** runtime (shipped with
Windows 10/11 and Microsoft Edge), so nothing extra needs bundling there
either.

Notes:

- macOS output: `dist/Gamdl GUI.app` (double-clickable).
- Windows output: `dist/Gamdl GUI/Gamdl GUI.exe` (the bundled `gamdl.exe` sits
  beside it; a console window is suppressed when it runs).
- External tools that gamdl shells out to — `ffmpeg`, `mp4decrypt`, `MP4Box`,
  `N_m3u8DL-RE` — are **not** statically linked; install them on the target
  machine (or point to them in **Advanced Settings → Paths & Tools**).
- If you prefer to use a `gamdl` you installed yourself (different version /
  venv), set its path under **Advanced Settings → Paths & Tools → gamdl
  Executable**; that always takes priority over the bundled one.

### Bundle size

The spec ships a custom hook (`packaging/hooks/hook-PySide6.QtGui.py`) that
drops two Qt plugins the app never uses:

| Plugin | Pulls in | Saved |
| --- | --- | --- |
| `imageformats/libqpdf` | QtPdf | ~8 MB |
| `platforminputcontexts/libqtvirtualkeyboardplugin` | QtVirtualKeyboard + QtQml + QtQuick | ~16 MB |

### Icon

An icon is included in `packaging/` (`icon.icns` / `icon.ico`) and picked up
automatically.  To regenerate or restyle it, edit and run:

```bash
python packaging/make_icon.py
```

It draws the artwork from scratch with Pillow (no font dependency); `.icns`
generation uses macOS `iconutil` and is skipped on other platforms.

## Legacy tkinter version

The original `customtkinter` GUI is kept in `legacy/gamdl_gui_ctk.py` for reference. It still works if you have the extra dependency installed:

```bash
pip install -r requirements-legacy.txt
python legacy/gamdl_gui_ctk.py
```
