#!/usr/bin/env python3
"""Calliper-measure the AP1 cluster against the OEM Car Spy photo.

Reads refs/oem/lit/lit_ap1_carspy_cluster.jpg, lets the operator click
landmarks with the mouse, then writes an annotated measurement plate
plus a JSON of every picked y-coordinate so the values can be re-applied
to refs/flat/DIMENSIONS.md.

Picking convention (per click, top-to-bottom):

    1.  cluster top edge   (just under the hood peak)
    2.  hood peak y        (top of the printed band arch)
    3.  band right end y   (where the redline blocks start at the 9 mark)
    4.  numeral 9 y        (centred on the digit, inside the well)
    5.  lamp strip top y   (top of the telltale / hardware strip)
    6.  cluster bottom y   (under the lamp strip, where the bezel ends)

Press 'q' to abort, 's' to save. Left-click to drop each landmark.

Output:
    refs/oem/plates/oem_ap1_measurements.json
    refs/oem/plates/oem_ap1_measurements_plate.png
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OEM = ROOT / "refs" / "oem" / "lit" / "lit_ap1_carspy_cluster.jpg"
PLATES = ROOT / "refs" / "oem" / "plates"

LANDMARKS: list[tuple[str, str]] = [
    ("cluster_top",  "cluster top edge (under the hood peak)"),
    ("hood_peak",    "hood peak y (top of the printed band arch)"),
    ("band_end",     "band right end y (where redline starts, ~9 mark)"),
    ("numeral_9",    "numeral 9 y (centred, inside the well)"),
    ("lamp_strip",   "lamp strip top y"),
    ("cluster_bot",  "cluster bottom y (under the lamp strip)"),
]


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for candidate in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSMono.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _pick_interactive() -> list[tuple[str, int]]:
    """Return [(name, y)] in display order. Driver outside PIL is fine; here
    we use the macOS `sips`-free approach: open the image in a Tk-free way
    by writing a tiny HTML viewer + reading the clicks back from a JSON
    sidecar.

    To keep this script zero-dep, we fall back to argparse-driven y values
    from the operator when the display isn't available (CI, ssh, etc.).
    """
    print(f"Open {OEM} in any image viewer that shows pixel coords.")
    print("Pick the following landmarks, top-to-bottom, and paste the y values:")
    picks: list[tuple[str, int]] = []
    for name, desc in LANDMARKS:
        print(f"  {name:>11}  {desc}")
        while True:
            raw = input(f"    y for {name} (px): ").strip()
            try:
                picks.append((name, int(raw)))
                break
            except ValueError:
                print("    integer required")
    return picks


def _annotate(img: Image.Image, picks: list[tuple[str, int]]) -> Image.Image:
    """Draw calliper guides and percentage labels."""
    canvas = img.convert("RGBA")
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font_label = _font(28)
    font_pct = _font(22)

    by = {name: y for name, y in picks}
    top = by["cluster_top"]
    bot = by["cluster_bot"]
    span = max(bot - top, 1)
    w, _ = canvas.size

    # Orange band over the cluster area
    draw.rectangle([0, top, w, bot], outline=(255, 168, 64, 255), width=4)

    for name, _ in LANDMARKS:
        y = by[name]
        # Full-width guide line
        draw.line([(0, y), (w, y)], fill=(140, 220, 255, 220), width=2)
        # Tiny notch at left
        draw.rectangle([0, y - 1, 22, y + 2], fill=(140, 220, 255, 255))
        # Label
        draw.text((28, y + 4), name, font=font_label, fill=(140, 220, 255, 255))

    # Percent table at the right
    pct_x = w - 360
    draw.text((pct_x, top + 8), "% of module height",
              font=font_label, fill=(255, 168, 64, 255))
    y = top + 48
    for name, _ in LANDMARKS:
        v = (by[name] - top) / span * 100
        draw.text((pct_x, y), f"{name:>11}  {v:5.1f}%",
                  font=font_pct, fill=(255, 232, 200, 255))
        y += 32

    # Caption
    draw.text((28, 16),
              "AP1 OEM calliper measurement — The Car Spy, CC BY 2.0",
              font=font_label, fill=(255, 168, 64, 255))

    return Image.alpha_composite(canvas, overlay)


def main() -> int:
    if not OEM.is_file():
        print(f"missing: {OEM}", file=sys.stderr)
        return 2
    PLATES.mkdir(parents=True, exist_ok=True)

    img = Image.open(OEM).convert("RGB")
    picks = _pick_interactive()

    plate = _annotate(img, picks)
    sidecar = {
        "source": str(OEM.relative_to(ROOT)),
        "image_size": list(img.size),
        "picks_px": picks,
    }
    by = {name: y for name, y in picks}
    top = by["cluster_top"]
    bot = by["cluster_bot"]
    span = bot - top
    sidecar["module_top_px"] = top
    sidecar["module_bottom_px"] = bot
    sidecar["module_height_px"] = span
    sidecar["pct_of_module_height"] = {
        name: round((y - top) / span * 100, 2) for name, y in picks
    }

    out_png = PLATES / "oem_ap1_measurements_plate.png"
    out_json = PLATES / "oem_ap1_measurements.json"
    plate.convert("RGB").save(out_png)
    out_json.write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out_png.relative_to(ROOT)}")
    print(f"wrote {out_json.relative_to(ROOT)}")
    print(json.dumps(sidecar["pct_of_module_height"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())