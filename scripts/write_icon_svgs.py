#!/usr/bin/env python3
"""Write AP1 telltale SVGs traced from OEM lamp-strip / self-test plates.

Source of truth is the OEM silhouettes (ISO 2575 wording + Honda AP1
pictograms), not crude boxes. Rasterise with ``scripts/rasterize_icons.py``.

Plates live in ``refs/oem/plates/`` (atlas + pictogram close-ups generated
from the Car Spy AP1 frame and the self-test lamp-strip descriptions).
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "icons"
HARNESS = ROOT / "apps" / "harness" / "public" / "icons"

HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" role="img" aria-label="{label}">
  <title>{label}</title>
  <!-- Traced / redrawn from OEM AP1 lamp-strip plates in refs/oem/plates/.
       White on transparent; tinted at draw time. Not Honda Motor Co. artwork. -->
'''
FOOT = "</svg>\n"


def wrap(name: str, body: str, vb_w: int = 64, vb_h: int = 48, label: str | None = None) -> str:
    return HEADER.format(vb_w=vb_w, vb_h=vb_h, label=label or name) + body + FOOT


# Word lamps: condensed bold gothic, matching the OEM printed legends.
WORD = (
    '  <text x="{x}" y="{y}" text-anchor="middle" fill="#fff" '
    'font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, Arial Narrow, sans-serif" '
    'font-size="{size}" font-weight="700" letter-spacing="{track}">{label}</text>\n'
)


SVGS: dict[str, str] = {
    "turn_l": wrap(
        "turn_l",
        '  <path fill="#fff" d="M51.2 6.8 2.4 24l48.8 17.2v-10.4H62V17.2H51.2z"/>\n',
        label="Left turn telltale",
    ),
    "turn_r": wrap(
        "turn_r",
        '  <path fill="#fff" d="M12.8 6.8v10.4H2v13.6h10.8v10.4L61.6 24z"/>\n',
        label="Right turn telltale",
    ),
    "high_beam": wrap(
        "high_beam",
        """  <g fill="#fff">
    <path d="M39.2 9c12.4 0 18.8 7.2 18.8 15s-6.4 15-18.8 15H32.4V9h6.8z"/>
    <rect x="4.4" y="11.4" width="24.2" height="2.5" rx="0.4"/>
    <rect x="2.4" y="16.8" width="26.2" height="2.5" rx="0.4"/>
    <rect x="2.4" y="22.2" width="26.2" height="2.5" rx="0.4"/>
    <rect x="2.4" y="27.6" width="26.2" height="2.5" rx="0.4"/>
    <rect x="4.4" y="33" width="24.2" height="2.5" rx="0.4"/>
  </g>
""",
        label="High beam telltale",
    ),
    "abs": wrap(
        "abs",
        WORD.format(x=32, y=31, size=17, track="0.8", label="ABS"),
        label="ABS telltale",
    ),
    "brake": wrap(
        "brake",
        WORD.format(x=48, y=31, size=16, track="1.0", label="BRAKE"),
        vb_w=96,
        label="BRAKE telltale",
    ),
    "battery": wrap(
        "battery",
        """  <g fill="#fff">
    <rect x="21.2" y="8.8" width="8.6" height="5.8" rx="0.6"/>
    <rect x="34.2" y="8.8" width="8.6" height="5.8" rx="0.6"/>
    <path fill-rule="evenodd" d="M12.6 15.4h38.8v23.6H12.6z M16.4 19h31.2v16.4H16.4z"/>
    <rect x="19.2" y="25.2" width="10.6" height="2.8"/>
    <rect x="23.1" y="21.2" width="2.8" height="10.8"/>
    <rect x="34.2" y="25.2" width="10.6" height="2.8"/>
  </g>
""",
        label="Battery telltale",
    ),
    "oil": wrap(
        "oil",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M5.2 24.4c0-7.4 5.4-12.8 13.4-12.8h6.2v5.4h-5.4c-4.2 0-7.2 3-7.2 7.4s3 7.4 7.2 7.4h5.4v5.4h-6.2C10.6 37.2 5.2 31.8 5.2 24.4z"/>
    <rect x="20.6" y="15.4" width="22.2" height="18.4" rx="1.2"/>
    <path d="M42.8 15.4 55.6 4.6l4.8 5.2-9.4 8.2z"/>
    <path d="M56.8 12.2c0 3.6 2.6 6.2 4.8 6.2s4.8-2.6 4.8-6.2c0-2.8-2.2-5.8-4.8-8.8-2.6 3-4.8 6-4.8 8.8z"/>
  </g>
""",
        label="Oil pressure telltale",
    ),
    "cel": wrap(
        "cel",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M18.2 9.6h19.6c1.4 0 2.6 0.9 3.1 2.2l2.4 6.6h9.6l4.8-5.4h5.6v7.6h3.2v12.6h-3.2v7.8H8.4v-7.8H2.6V27.8h5.8v-4.6h7.4L16.8 11.8c0.5-1.3 1.7-2.2 3.1-2.2z M17.2 24.8h30.8v8.4H17.2z"/>
    <path d="M19.6 26.4h3.2v5.2h-3.2zm6.2 0h3.2v5.2h-3.2zm6.2 0h3.2v5.2h-3.2zm6.2 0h3.2v5.2h-3.2zm6.2 0h3.2v5.2h-3.2z"/>
  </g>
""",
        label="Check engine telltale",
    ),
    "immobilizer": wrap(
        "immobilizer",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M16.8 10.8a12.2 12.2 0 1 0 .02 0zm0 5.8a6.4 6.4 0 1 0 .02 0z"/>
    <rect x="26.2" y="20.2" width="30.2" height="6.6" rx="1"/>
    <rect x="43.8" y="26.8" width="4.4" height="8.4" rx="0.5"/>
    <rect x="50.6" y="26.8" width="4.4" height="11.6" rx="0.5"/>
  </g>
""",
        label="Immobilizer key telltale",
    ),
    "maint": wrap(
        "maint",
        WORD.format(x=32, y="20.5", size=13, track="0.35", label="MAINT")
        + WORD.format(x=32, y="36.5", size=13, track="0.15", label="REQ'D"),
        label="MAINT REQ'D telltale",
    ),
    "eps": wrap(
        "eps",
        WORD.format(x=32, y=31, size=17, track="0.8", label="EPS"),
        label="EPS telltale",
    ),
    "seatbelt": wrap(
        "seatbelt",
        """  <g fill="#fff">
    <circle cx="32" cy="8.2" r="6.4"/>
    <path fill-rule="evenodd" d="M18.4 17.8c0-2.2 5.8-4.4 13.6-4.4s13.6 2.2 13.6 4.4V43.6H18.4z M21.2 16.8 45.6 43.6h-8.8L19.4 23.6z"/>
  </g>
""",
        label="Seatbelt telltale",
    ),
    "door": wrap(
        "door",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M25.4 3h13.2c1.4 0 2.7.7 3.5 1.8l4.8 6.2v27.2c0 1.4-.7 2.7-1.8 3.5l-6.2 4.8H25.1l-6.2-4.8c-1.1-.8-1.8-2.1-1.8-3.5V11c0-1.4.7-2.7 1.8-3.5z M28.2 10.2h7.6v6.2h-7.6z"/>
    <path d="M17.2 19.8 2.6 27.4l3.8 5.8 12.4-6.6z"/>
    <path d="M46.8 19.8 61.4 27.4l-3.8 5.8-12.4-6.6z"/>
  </g>
""",
        label="Door-open telltale",
    ),
    "srs": wrap(
        "srs",
        WORD.format(x=32, y=31, size=17, track="0.8", label="SRS"),
        label="SRS telltale",
    ),
}

ATLAS = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 72" width="980" height="72" role="img" aria-label="AP1 OEM lamp atlas">
  <title>AP1 OEM lamp atlas — self-test order</title>
  <rect width="980" height="72" fill="#0a0a0a"/>
  <g transform="translate(8,16)" fill="#28c85c"><path d="M34 6 6 24l28 18v-10h10V16H34z"/></g>
  <g transform="translate(52,16)" fill="#2460e4">
    <path d="M28 8c9 0 14 6.4 14 10.4S37 28.8 28 28.8h-4V8h4z"/>
    <path d="M4 11h18M2 15.2h20M2 19.2h20M2 23.2h20M4 27.2h18" stroke="#2460e4" stroke-width="2.2" fill="none"/>
  </g>
  <text x="130" y="44" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="18" font-weight="700" fill="#ec941c">ABS</text>
  <text x="210" y="44" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="18" font-weight="700" fill="#e22820">BRAKE</text>
  <g transform="translate(268,16)" fill="#e22820">
    <rect x="6" y="2" width="6" height="4" rx="0.4"/>
    <rect x="16" y="2" width="6" height="4" rx="0.4"/>
    <path fill-rule="evenodd" d="M2 8h24v16H2z M4 10.4h20v11.2H4z"/>
    <rect x="6" y="15" width="6" height="2"/>
    <rect x="15" y="15" width="6" height="2"/>
    <rect x="17.2" y="12.4" width="1.8" height="7.2"/>
  </g>
  <g transform="translate(316,14)" fill="#e22820">
    <path fill-rule="evenodd" d="M2.2 18.4c0-5.2 3.8-9 9.4-9h4.4v3.8h-3.8c-3 0-5 2.1-5 5.2s2 5.2 5 5.2h3.8V27h-4.4c-5.6 0-9.4-3.8-9.4-8.6z"/>
    <rect x="13.2" y="12" width="15.6" height="13" rx="0.8"/>
    <path d="M28.8 12 38.2 4.4l3.4 3.6-6.6 5.8z"/>
    <path d="M39.2 9.8c0 2.6 1.8 4.4 3.4 4.4s3.4-1.8 3.4-4.4c0-2-1.6-4.2-3.4-6.4-1.8 2.2-3.4 4.4-3.4 6.4z"/>
  </g>
  <g transform="translate(360,14)" fill="#ec941c">
    <path d="M4 16h5l2.4-5.2h7l1.6 5.2h12l2.6-3.4H38v5.4h2.4v9H38V36H4v-4H1.2v-8.2H4z"/>
    <rect x="12" y="20" width="20" height="5.6" fill="#0a0a0a"/>
    <text x="22" y="25" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="6" font-weight="800" fill="#ec941c">CHECK</text>
  </g>
  <g transform="translate(414,16)" fill="#28c85c">
    <path fill-rule="evenodd" d="M10 6.2a8.4 8.4 0 1 0 .01 0zm0 4.2a4.2 4.2 0 1 0 .01 0z"/>
    <rect x="16" y="13" width="18" height="5.2" rx="0.5"/>
    <rect x="27" y="18" width="2.8" height="6"/>
    <rect x="31.6" y="18" width="2.8" height="8.2"/>
  </g>
  <text x="500" y="32" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#ec941c">MAINT</text>
  <text x="500" y="48" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#ec941c">REQ'D</text>
  <text x="568" y="44" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="16" font-weight="700" fill="#ec941c">EPS</text>
  <g transform="translate(600,10)" fill="#e22820">
    <circle cx="22" cy="8.6" r="5.5"/>
    <path fill-rule="evenodd" d="M11 18.4c0-2 3.2-3.6 11-3.6s11 1.6 11 3.6V40H11z M13.4 17.2 33.6 40h-7.4L12.2 22.4z"/>
  </g>
  <g transform="translate(652,8)" fill="#e22820">
    <path fill-rule="evenodd" d="M18.4 6h13.2l5.6 6.2v24.4L31.6 43H18.4l-5.6-6.4V12.2z M21.6 12h6.8v5H21.6z"/>
    <path d="M13 20 4.2 25.4l2.2 3.4 8.6-4.6z"/>
    <path d="M37 20l8.8 5.4-2.2 3.4-8.6-4.6z"/>
  </g>
  <text x="760" y="44" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="16" font-weight="700" fill="#e22820">SRS</text>
  <g transform="translate(800,16)" fill="#28c85c"><path d="M10 6v9H0v12h10v9l28-15z"/></g>
</svg>
'''


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name, svg in SVGS.items():
        path = DEST / f"{name}.svg"
        path.write_text(svg, encoding="utf-8")
        written.append(path)
        print(path.relative_to(ROOT))
    atlas = DEST / "atlas.svg"
    atlas.write_text(ATLAS, encoding="utf-8")
    written.append(atlas)
    print(atlas.relative_to(ROOT))
    if HARNESS.is_dir():
        for path in written:
            dest = HARNESS / path.name
            shutil.copy2(path, dest)
            print(dest.relative_to(ROOT))


if __name__ == "__main__":
    main()
