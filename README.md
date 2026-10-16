# Gamdl GUI

Gamdl GUI is a modern, user-friendly graphical interface for [gamdl](https://github.com/glomatico/gamdl) (an Apple Music Downloader). It provides an easy way to download songs, albums, playlists, and music videos from Apple Music without needing to use the command line directly.

<img width="800" height="1356" alt="image" src="https://github.com/user-attachments/assets/da27eb86-1c9d-455b-b0d8-6bdbc14422a2" />


## Features

- **Modern interface**: built with **PySide6 (Qt)** — native widgets, resizable layout and a dark/light/system theme.
- **Easy cookie management**: sign in to Apple Music in a built-in webview and the app captures the required cookie automatically — or import a `cookies.txt` manually (the previous file is backed up).
- **Batch downloading**: paste multiple Apple Music URLs (songs, albums, playlists, stations, artists, videos) and download them all at once.
- **Real-time console**: gamdl's coloured log is rendered inline, with a reliable progress bar and current-track label.
- **Full gamdl option coverage** (gamdl **3.x**):
  - Download mode (`ytdlp` / `nm3u8dlre`) and log level.
  - **Song codec priority** — `alac` for lossless, or the various AAC/Atmos/AC3 codecs.
  - Metadata **language**, album-release-date tagging, date-tag template, artist auto-select.
  - Cover image options (format / size), M3U8 playlist export, filename truncation, tag exclusion.
  - Synced-lyrics format (`lrc`/`srt`/`ttml`) and lyrics-only mode.
  - Music-video resolution / codec / remux format, post-video quality.
  - **Folder & file naming templates** (album, compilation, playlist, single/multi-disc, …).
  - **DRM backend** (`widevine` / `playready`) with `.wvd` / `.prd` device files.
  - Download database (SQLite) for tracking downloaded media.
  - Temp directory, log file and external tool paths (ffmpeg, N_m3u8DL-RE).
  - **Wrapper decryption** settings (`--use-wrapper`, URL, decrypt host/port).
- **Remembers everything**: output directory, log level, download mode, checkboxes, language, theme and window size are saved to `config.json`.
- **Multi-language UI**: English / 中文, switchable on the fly.

## Prebuilt downloads

Tagged [releases](https://github.com/carlchina/Gamdl_GUI/releases) contain
ready-to-run bundles — no Python and no `gamdl` installation needed:

| Platform | Full (embedded sign-in) | Lite (manual `cookies.txt`) |
| --- | --- | --- |
| macOS 11+ · Apple silicon | `Gamdl-GUI-macOS-arm64.zip` | `Gamdl-GUI-macOS-arm64-lite.zip` |
| macOS 11+ · Intel | `Gamdl-GUI-macOS-x86_64.zip` | `Gamdl-GUI-macOS-x86_64-lite.zip` |
| Windows 10/11 · x64 | `Gamdl-GUI-Windows-x64.zip` | `Gamdl-GUI-Windows-x64-lite.zip` |

Unzip it and run. The **lite** bundles leave out the embedded sign-in webview;
use **Import cookies.txt** there instead.

> **macOS first launch.** The bundles are ad-hoc signed only (no Apple
> Developer ID / notarisation), so Gatekeeper refuses the first launch. Either
> right-click the app → **Open** → **Open**, or clear the quarantine flag once:
>
> ```bash
> xattr -dr com.apple.quarantine "/path/to/Gamdl GUI.app"
> ```

Each release also ships `SHA256SUMS.txt`.

## Prerequisites

1. **Python 3.10** or higher (gamdl itself requires ≥ 3.10).
2. **gamdl 3.9 or newer** — the core downloader:
   ```bash
   pip install -U gamdl
   ```
   *Note: gamdl 3.x muxes and decrypts internally with a bundled Rust engine, so `MP4Box` / `mp4decrypt` are **no longer needed**. Only the optional [`N_m3u8DL-RE`](https://github.com/nilaoda/N_m3u8DL-RE) download mode additionally needs `ffmpeg`. See the [gamdl documentation](https://github.com/glomatico/gamdl) for details.*

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
├── .github/workflows/build.yml # CI: builds + releases every platform
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
small — on macOS it measured **≈ +5 MB (119 MB → 124 MB)**, versus roughly
+200 MB for a QtWebEngine-based approach.

On Windows the sign-in window relies on the **WebView2** runtime (shipped with
Windows 10/11 and Microsoft Edge), so nothing extra needs bundling there
either.

Notes:

- macOS output: `dist/Gamdl GUI.app` (double-clickable).
- Windows output: `dist/Gamdl GUI/Gamdl GUI.exe` (the bundled `gamdl.exe` sits
  beside it; a console window is suppressed when it runs).
- External tools — gamdl 3.x bundles its own Rust muxer/decryptor, so
  `MP4Box` / `mp4decrypt` are no longer required. Only `ffmpeg` (for the
  `nm3u8dlre` download mode) and optionally `N_m3u8DL-RE` need to be available;
  point to them in **Advanced Settings → Paths & Tools** if they are not on
  `PATH`.
- If you prefer to use a `gamdl` you installed yourself (different version /
  venv), set its path under **Advanced Settings → Paths & Tools → gamdl
  Executable**; that always takes priority over the bundled one.
- The GUI always launches gamdl with `--no-config-file`, because every option
  is owned by the GUI (`config.json` / Advanced Settings) and should never be
  overridden by a stray `~/.gamdl/config.ini`.

### Bundle size

Two things keep the download small. The spec ships a custom hook
(`packaging/hooks/hook-PySide6.QtGui.py`) that drops two Qt plugins the app
never uses:

| Plugin | Pulls in | Saved |
| --- | --- | --- |
| `imageformats/libqpdf` | QtPdf | ~8 MB |
| `platforminputcontexts/libqtvirtualkeyboardplugin` | QtVirtualKeyboard + QtQml + QtQuick | ~16 MB |

…and it excludes the optional accelerators, unused integrations and transitive
leftovers that static analysis pulls in. Each one is safe because the library
that references it guards the import behind a `try/except ImportError` (or the
code path is never reached at all):

| Excluded | Why it is safe |
| --- | --- |
| `numpy` | `construct` (via gamdl) guards the import |
| `simplejson` | `requests` falls back to the stdlib `json` |
| `zstandard` | `httpx` / `urllib3` fall back to stdlib zlib |
| `Cryptodome` | yt-dlp falls back to `Crypto` (kept) or its native AES |
| `twisted`, `zope`, `automat`, `constantly`, `hyperlink`, `incremental` | only structlog's unused Twisted integration needs them |
| `uvloop`, `tornado`, `psutil`, `yaml`, `markupsafe`, `service_identity` | never imported by the app or any of its dependencies |
| `pytest`, `_pytest`, `pkg_resources`, `setuptools`, `wheel`, `pip` | test/packaging machinery only — see the note below |

> **Why `pkg_resources` has to be excluded, not just left out.** Static analysis
> finds a conditional `from pkg_resources import fixup_namespace_packages` inside
> `_pytest/monkeypatch.py`, which drags `pkg_resources` into the module graph.
> PyInstaller reacts to that module by attaching its `pyi_rth_pkgres` run-time
> hook, and that hook imports `pkg_resources` — which since setuptools 71 runs
> `from jaraco.text import ...`. `jaraco` only exists vendored inside
> `setuptools/_vendor`, so the import fails and *every* frozen executable dies
> before `main()` with `ModuleNotFoundError: No module named 'jaraco'`.
> Excluding `pkg_resources` also drops the hook, because excluded modules are
> `ExcludedModule` nodes and those are not part of the TOC the hook list is built
> from.

Measured on macOS arm64: the webview bundle went **146 MB → 124 MB**, and the
lite bundle is **119 MB**.

### Continuous integration & releases

`.github/workflows/build.yml` builds all six bundles on the **native** runner
for each platform — `macos-15` (arm64), `macos-15-intel` (x86_64) and
`windows-latest` (x64), each in a `webview` and a `lite` variant. It smoke-tests
the bundled downloader (`gamdl --version`), zips the result, and when it runs
for a `v*` tag it publishes everything to a GitHub release along with
`SHA256SUMS.txt`. You can also start it by hand from the **Actions** tab to get
artifacts without publishing anything.

macOS bundles are packed with `ditto` so the `.app` symlinks and signature
survive; on Windows the `dist/Gamdl GUI` folder is zipped as-is.

Releasing is therefore just:

```bash
git tag v1.0.0
git push origin v1.0.0
```

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
