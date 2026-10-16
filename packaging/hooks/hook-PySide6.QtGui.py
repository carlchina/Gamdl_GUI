"""Custom ``PySide6.QtGui`` hook (overrides PyInstaller's built-in one).

The built-in hook collects the ``imageformats`` and ``platforminputcontexts``
Qt plugin folders.  Two of those plugins drag in Qt stacks this app never uses:

* ``imageformats/libqpdf``            -> QtPdf         (~8 MB)
* ``platforminputcontexts/libqtvirtualkeyboardplugin`` -> QtVirtualKeyboard
  -> QtQml + QtQuick + QtQml*        (~16 MB)

Dropping the two plugin files keeps PyInstaller's binary dependency scan from
pulling those frameworks, shrinking the bundle without touching anything the
GUI actually needs.
"""

import os

from PyInstaller.utils.hooks.qt import add_qt6_dependencies

hiddenimports, binaries, datas = add_qt6_dependencies(__file__)

_EXCLUDED_PLUGINS = ("libqpdf", "libqtvirtualkeyboardplugin")


def _keep(entry):
    return not any(token in os.path.basename(entry[0]) for token in _EXCLUDED_PLUGINS)


binaries = [binary for binary in binaries if _keep(binary)]
datas = [data for data in datas if _keep(data)]
