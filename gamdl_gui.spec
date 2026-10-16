# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Gamdl GUI.

Builds a single onedir bundle that contains **two** executables sharing one
set of dependencies:

* ``Gamdl GUI`` (windowed) - the Qt interface,
* ``gamdl``     (console) - the downloader engine, bundled so the packaged
  app is self-contained.

``gamdl_gui/core/gamdl.py`` finds the bundled ``gamdl`` automatically at
runtime.  Build with::

    python packaging/build.py                 # lite build
    python packaging/build.py --webview       # + embedded sign-in

or directly::

    pyinstaller --noconfirm --clean gamdl_gui.spec

Set ``GAMDL_GUI_WEBVIEW=1`` in the environment to include the optional
pywebview-based "Sign in to Apple Music" flow (``packaging/build.py --webview``
does this for you).
"""

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

APP_NAME = "Gamdl GUI"
BUNDLE_ID = "com.carlchina.gamdlgui"
SPEC_DIR = Path(SPECPATH).resolve()  # noqa: F821  (injected by PyInstaller)

# Optional embedded sign-in (pywebview). Build with ``GAMDL_GUI_WEBVIEW=1``
# (or ``python packaging/build.py --webview``) to include it; the default lite
# build omits it and falls back to manual cookies.txt import.
WITH_WEBVIEW = os.environ.get("GAMDL_GUI_WEBVIEW") == "1"

# --- resources -------------------------------------------------------------
datas = [(str(SPEC_DIR / "langs"), "langs")]

gamdl_hidden = collect_submodules("gamdl")

webview_hidden = []
webview_excludes = ["webview", "qtpy", "PyQt5", "PyQt6", "PySide2"]
if WITH_WEBVIEW:
    webview_hidden = collect_submodules("webview")
    # pywebview's ``guilib.py`` imports every backend in a branch, so
    # ``webview.platforms.qt`` always ends up in the graph and pulls in
    # ``qtpy`` -> PyQt5.  PyInstaller refuses to freeze two Qt bindings
    # (we ship PySide6), so the stray bindings must be excluded.  Only the
    # OS-native backend is ever imported at run time.
    webview_excludes = ["qtpy", "PyQt5", "PyQt6", "PySide2"]
    datas += collect_data_files("webview")

# --- icons (optional) ------------------------------------------------------
icon_mac = SPEC_DIR / "packaging" / "icon.icns"
icon_win = SPEC_DIR / "packaging" / "icon.ico"
icon = None
if sys.platform == "darwin" and icon_mac.exists():
    icon = str(icon_mac)
elif sys.platform == "win32" and icon_win.exists():
    icon = str(icon_win)

common_excludes = ["tkinter", "customtkinter", "test", "unittest", "pydoc"]

# --- the Qt GUI ------------------------------------------------------------
gui_analysis = Analysis(  # noqa: F821
    [str(SPEC_DIR / "main.py")],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=webview_hidden,
    hookspath=[str(SPEC_DIR / "packaging" / "hooks")],
    hooksconfig={},
    runtime_hooks=[],
    excludes=common_excludes + webview_excludes,
    noarchive=False,
    optimize=0,
)

# --- the bundled gamdl CLI -------------------------------------------------
cli_analysis = Analysis(  # noqa: F821
    [str(SPEC_DIR / "packaging" / "gamdl_cli.py")],
    pathex=[str(SPEC_DIR)],
    binaries=[],
    datas=[],
    hiddenimports=gamdl_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "customtkinter", "PySide6", "pydoc"],
    noarchive=False,
    optimize=0,
)

# Share modules between the two executables so they are stored once.
MERGE(  # noqa: F821
    (gui_analysis, APP_NAME, APP_NAME),
    (cli_analysis, "gamdl", "gamdl"),
)

gui_pyz = PYZ(gui_analysis.pure)  # noqa: F821
cli_pyz = PYZ(cli_analysis.pure)  # noqa: F821

gui_exe = EXE(  # noqa: F821
    gui_pyz,
    gui_analysis.scripts,
    [],
    exclude_binaries=True,
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon,
)

cli_exe = EXE(  # noqa: F821
    cli_pyz,
    cli_analysis.scripts,
    [],
    exclude_binaries=True,
    name="gamdl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(  # noqa: F821
    gui_exe,
    gui_analysis.binaries,
    gui_analysis.datas,
    cli_exe,
    cli_analysis.binaries,
    cli_analysis.datas,
    strip=False,
    upx=False,
    name=APP_NAME,
)

if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        coll,
        name=f"{APP_NAME}.app",
        icon=str(icon_mac) if icon_mac.exists() else None,
        bundle_identifier=BUNDLE_ID,
        info_plist={
            "CFBundleName": APP_NAME,
            "CFBundleDisplayName": APP_NAME,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "10.15",
        },
    )
