# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Gamdl GUI.

Builds a single onedir bundle that contains **two** executables sharing one
set of dependencies:

* ``Gamdl GUI`` (windowed) - the Qt interface,
* ``gamdl``     (console) - the downloader engine, bundled so the packaged
  app is self-contained.

``gamdl_gui/core/gamdl.py`` finds the bundled ``gamdl`` automatically at
runtime.  Build with::

    python packaging/build.py                 # without the sign-in flow
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

from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

APP_NAME = "Gamdl GUI"
BUNDLE_ID = "com.carlchina.gamdlgui"
SPEC_DIR = Path(SPECPATH).resolve()  # noqa: F821  (injected by PyInstaller)

# Optional embedded sign-in (pywebview). Build with ``GAMDL_GUI_WEBVIEW=1``
# (or ``python packaging/build.py --webview``) to include it; without it the
# sign-in button is hidden and manual cookies.txt import is used.
WITH_WEBVIEW = os.environ.get("GAMDL_GUI_WEBVIEW") == "1"

# --- resources -------------------------------------------------------------
datas = [(str(SPEC_DIR / "langs"), "langs")]

gamdl_hidden = collect_submodules("gamdl")
# gamdl 3.x ships a compiled Rust muxer/decryptor (``gamdl/_ammuxer.abi3.so``).
# It is picked up through ``collect_submodules`` too, but collecting the shared
# library explicitly guarantees it lands in the bundle.
gamdl_binaries = collect_dynamic_libs("gamdl")

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

# Modules that are never reached at run time.  Most of them are optional
# accelerators guarded by ``try/except ImportError`` in the library that uses
# them, so dropping them simply selects a pure-Python fallback; the rest are
# transitive leftovers or packaging-only helpers.  Besides trimming ~15 MB this
# also stops several single-architecture-only C extensions from being pulled
# in (numpy, zstandard, ...).
optional_excludes = [
    # guarded optional accelerators -> pure-Python fallback
    "numpy",        # construct (via gamdl) guards the import
    "simplejson",   # requests falls back to the stdlib json module
    "zstandard",    # httpx / urllib3 fall back to stdlib
    "Cryptodome",   # yt-dlp falls back to Crypto (kept) or its own native AES
    # only reachable from code paths this app never runs
    "twisted", "automat", "constantly", "hyperlink", "incremental", "zope",
    "uvloop", "tornado", "psutil", "yaml", "markupsafe", "service_identity",
    # pytest is dragged in by a stray static reference inside
    # ``_pytest.monkeypatch``; ``pkg_resources`` comes along with it and is the
    # reason it has to go: PyInstaller reacts to that module by attaching its
    # ``pyi_rth_pkgres`` run-time hook, which immediately imports
    # ``pkg_resources`` -> ``jaraco.text``.  Since setuptools >= 71 only vendors
    # jaraco inside ``setuptools/_vendor`` (excluded below as well), that import
    # fails and every frozen executable dies on start-up with
    # ``ModuleNotFoundError: No module named 'jaraco'``.  Excluded modules are
    # ``ExcludedModule`` nodes, which are not part of the TOC the hook list is
    # built from, so excluding ``pkg_resources`` drops the hook too.
    "pytest", "_pytest", "pluggy", "iniconfig", "pkg_resources",
    "setuptools", "wheel", "pip",
    # packaging tools / command-line entry points we never invoke
    "PySide6.scripts", "pywidevine.main", "pyplayready.main",
]

common_excludes = ["tkinter", "customtkinter", "test", "unittest", "pydoc"] + optional_excludes

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
    binaries=gamdl_binaries,
    datas=[],
    hiddenimports=gamdl_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "customtkinter", "PySide6", "pydoc"] + optional_excludes,
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
