#!/usr/bin/env python3
"""Generate the application icon.

Produces, next to this script:

* ``icon.png``  - 1024x1024 master image
* ``icon.icns`` - macOS icon (built with ``iconutil``, skipped elsewhere)
* ``icon.ico``  - Windows icon (multi-size)

The artwork is drawn from scratch with Pillow (no font/glyph dependency): a
rounded Apple-Music-style gradient tile with white beamed eighth notes.

Usage::

    python packaging/make_icon.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SIZE = 1024
SS = 4  # supersampling factor

TOP = (255, 94, 126)  # #FF5E7E
BOTTOM = (247, 33, 66)  # #F72142

# Rounded-tile geometry (macOS "squircle" look): art is inset on the canvas.
INSET = 0.075
CORNER = 0.2237  # corner radius as a fraction of the art size


def _vertical_gradient(width: int, height: int, top: tuple, bottom: tuple) -> Image.Image:
    gradient = Image.new("RGB", (1, height))
    for y in range(height):
        t = y / (height - 1)
        gradient.putpixel(
            (0, y),
            tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)),
        )
    return gradient.resize((width, height))


def _rounded_mask(size: int, radius: int) -> Image.Image:
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return mask


def _draw_notes(size: int) -> Image.Image:
    """Two beamed eighth notes, drawn white-on-transparent."""
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    white = (255, 255, 255, 255)

    head_rx, head_ry = 0.100 * size, 0.078 * size
    baseline = 0.690 * size
    head1_x, head2_x = 0.345 * size, 0.615 * size
    stem_w = 0.042 * size
    stem1_x = head1_x + 0.062 * size
    stem2_x = head2_x + 0.062 * size
    beam_h = 0.100 * size

    # stems (right stem slightly shorter -> slanted beam)
    beam1_y = 0.245 * size
    beam2_y = 0.290 * size
    draw.rectangle([stem1_x, beam1_y, stem1_x + stem_w, baseline], fill=white)
    draw.rectangle([stem2_x, beam2_y, stem2_x + stem_w, baseline], fill=white)

    # beam joining the stems
    draw.polygon(
        [
            (stem1_x, beam1_y),
            (stem2_x + stem_w, beam2_y),
            (stem2_x + stem_w, beam2_y + beam_h),
            (stem1_x, beam1_y + beam_h),
        ],
        fill=white,
    )

    # note heads (rotated for a livelier look)
    for head_x in (head1_x, head2_x):
        head = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(head).ellipse(
            [head_x - head_rx, baseline - head_ry, head_x + head_rx, baseline + head_ry],
            fill=white,
        )
        head = head.rotate(-20, resample=Image.BICUBIC, center=(head_x, baseline))
        layer.alpha_composite(head)

    return layer


def build_master() -> Image.Image:
    canvas = SIZE * SS
    art = round(canvas * (1 - 2 * INSET))

    tile = _vertical_gradient(art, art, TOP, BOTTOM).convert("RGBA")

    notes = _draw_notes(art)

    # soft drop shadow under the notes
    shadow = Image.new("RGBA", (art, art), (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 110), (0, 0), notes.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.014 * art))
    tile.alpha_composite(shadow, (0, round(0.014 * art)))
    tile.alpha_composite(notes)

    tile.putalpha(_rounded_mask(art, round(CORNER * art)))

    master = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    master.alpha_composite(tile, (round(canvas * INSET), round(canvas * INSET)))
    return master.resize((SIZE, SIZE), Image.LANCZOS)


def write_png(master: Image.Image) -> Path:
    path = HERE / "icon.png"
    master.save(path)
    return path


def write_ico(master: Image.Image) -> Path:
    path = HERE / "icon.ico"
    master.save(path, sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    return path


def write_icns(master: Image.Image) -> Path | None:
    if sys.platform != "darwin" or shutil.which("iconutil") is None:
        return None

    iconset = HERE / "icon.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir()

    specs = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]
    for name, px in specs:
        master.resize((px, px), Image.LANCZOS).save(iconset / name)

    icns = HERE / "icon.icns"
    subprocess.check_call(["iconutil", "-c", "icns", str(iconset), "-o", str(icns)])
    shutil.rmtree(iconset)
    return icns


def main() -> int:
    master = build_master()
    print("wrote", write_png(master))
    print("wrote", write_ico(master))
    icns = write_icns(master)
    if icns:
        print("wrote", icns)
    else:
        print("skipped .icns (needs macOS + iconutil)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
