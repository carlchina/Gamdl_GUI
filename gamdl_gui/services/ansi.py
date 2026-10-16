"""Convert the ANSI escape codes gamdl/click/colorama emit into Qt rich text.

The old implementation only understood foreground SGR codes and hacked around
the erase-line sequence by rewriting ``K`` into ``m``.  This module handles the
common SGR codes (reset, muted, bold, 30-37, 90-97) and simply strips anything
else so no stray ``\\x1b[`` ever shows up in the console.
"""

from __future__ import annotations

import re
from html import escape

_SGR_RE = re.compile(r"\x1b\[([0-9;]*)m")
_ANY_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

# Dracula-ish palette, matching the look of the old GUI.
_COLORS = {
    "30": "#6272A4",
    "31": "#FF5555",
    "32": "#50FA7B",
    "33": "#F1FA8C",
    "34": "#BD93F9",
    "35": "#FF79C6",
    "36": "#8BE9FD",
    "37": "#F8F8F2",
    "90": "#6272A4",
    "91": "#FF6E6E",
    "92": "#69FF94",
    "93": "#FFFFA5",
    "94": "#D6ACFF",
    "95": "#FF92DF",
    "96": "#A4FFFF",
    "97": "#FFFFFF",
}


def strip_ansi(text: str) -> str:
    """Return *text* with every ANSI escape sequence removed."""
    text = _SGR_RE.sub("", text)
    return _ANY_ANSI_RE.sub("", text)


def _wrap(text: str, color: str | None, bold: bool) -> str:
    if not color and not bold:
        return text
    styles = []
    if color:
        styles.append(f"color:{color}")
    if bold:
        styles.append("font-weight:bold")
    return f'<span style="{";".join(styles)}">{text}</span>'


def ansi_to_html(text: str) -> str:
    """Convert a single line containing SGR codes into an HTML fragment."""
    parts: list[str] = []
    color: str | None = None
    bold = False
    pos = 0

    for match in _SGR_RE.finditer(text):
        chunk = text[pos:match.start()]
        if chunk:
            parts.append(_wrap(escape(chunk), color, bold))
        pos = match.end()
        for code in match.group(1).split(";"):
            if code in ("", "0"):
                color, bold = None, False
            elif code == "1":
                bold = True
            elif code == "22":
                bold = False
            elif code == "39":
                color = None
            elif code in _COLORS:
                color = _COLORS[code]
            # any other code (background, erase-line, ...) is ignored

    tail = text[pos:]
    if tail:
        # Remove any non-SGR sequences (e.g. erase-line) before rendering.
        tail = _ANY_ANSI_RE.sub("", tail)
        parts.append(_wrap(escape(tail), color, bold))

    return "".join(parts) or escape(text)
