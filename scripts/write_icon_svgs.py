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
    'font-family="DejaVu Sans, Liberation Sans, Arial Narrow, sans-serif" '
    'font-size="{size}" font-weight="700" letter-spacing="{track}">{label}</text>\n'
)


SVGS: dict[str, str] = {
    "turn_l": wrap(
        "turn_l",
        '  <path fill="#fff" d="M46 8.5 7 24l39 15.5v-8.2h13.5V16.7H46z"/>\n',
        label="Left turn telltale",
    ),
    "turn_r": wrap(
        "turn_r",
        '  <path fill="#fff" d="M18 8.5v8.2H4.5v14.6H18v8.2L57 24z"/>\n',
        label="Right turn telltale",
    ),
    "high_beam": wrap(
        "high_beam",
        """  <path fill="#fff" d="M38 10c12.4 0 19.2 8.1 19.2 14S50.4 38 38 38h-6.4V10H38z"/>
  <path fill="#fff" d="M6 13.2h23.5v2.7H6zm-2 5.2h25.5v2.7H4zm0 5.2h25.5v2.7H4zm0 5.2h25.5v2.7H4zm2 5.2h23.5v2.7H6z"/>
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
    <rect x="21.5" y="10.5" width="8.2" height="5.6" rx="0.6"/>
    <rect x="34.3" y="10.5" width="8.2" height="5.6" rx="0.6"/>
    <path fill-rule="evenodd" d="M13.5 16.2h37v22.2h-37z M16.4 19.1h31.2v16.4H16.4z"/>
    <rect x="19.6" y="25.6" width="10.2" height="2.7"/>
    <rect x="23.3" y="21.6" width="2.8" height="10.7"/>
    <rect x="34.2" y="25.6" width="10.2" height="2.7"/>
  </g>
""",
        label="Battery telltale",
    ),
    "oil": wrap(
        "oil",
        """  <g fill="#fff">
    <path d="M9.2 23.6c0-3.4 2.4-6.2 6.4-6.2H20v18.6h-6.2c-2.4 0-4.6-2.8-4.6-12.4z"/>
    <rect x="20" y="17.4" width="18.4" height="18.8"/>
    <path d="M38.4 17.4 54.8 5.2l3.8 3.7-11.2 8.8v18.5H38.4z"/>
    <path d="M52.6 16.2c0 3.8 2.8 6.8 5.4 6.8s5.4-3 5.4-6.8c0-3.2-2.6-6.1-5.4-9.3-2.8 3.2-5.4 6.1-5.4 9.3z"/>
  </g>
""",
        label="Oil pressure telltale",
    ),
    "cel": wrap(
        "cel",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M8.2 20.4h7.4l3.3-7.8h14.2l2.3 7.8H50.6l4.6-5.2h5.2v7.6h2.6v13.2h-2.6v8.2H8.2v-8.2H3.4V29.2h4.8z M17.4 26.2h29.4v7.4H17.4z"/>
    <path d="M19.6 27.6h3.2v4.6h-3.2zm5.4 0h3.2v4.6h-3.2zm5.4 0h3.2v4.6h-3.2zm5.4 0h3.2v4.6h-3.2zm5.4 0h3.2v4.6h-3.2z"/>
  </g>
""",
        label="Check engine telltale",
    ),
    "immobilizer": wrap(
        "immobilizer",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M18 13.2a10.8 10.8 0 1 0 0.01 0zm0 5.2a5.6 5.6 0 1 0 0.01 0z"/>
    <rect x="26.2" y="20.8" width="26.6" height="6.6" rx="0.8"/>
    <rect x="41.4" y="27.2" width="3.8" height="7.4" rx="0.4"/>
    <rect x="47.6" y="27.2" width="3.8" height="10.2" rx="0.4"/>
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
    <circle cx="32" cy="9.4" r="6.5"/>
    <path fill-rule="evenodd" d="M17.6 19.8c0-2.5 4.5-5 14.4-5s14.4 2.5 14.4 5V43.2H17.6z M20.2 18.4 45.4 43.2h-9.2L18.8 24.6z"/>
  </g>
""",
        label="Seatbelt telltale",
    ),
    "door": wrap(
        "door",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M25.4 4.6h13.2c1.2 0 2.4 0.6 3.2 1.6l4.8 6.4v26.2c0 1.2-0.6 2.4-1.6 3.2L38.6 47.4H25.4l-6.4-5.4c-1-0.8-1.6-2-1.6-3.2V12.6c0-1.2 0.6-2.4 1.6-3.2z M28.2 10.8h7.6v6.4h-7.6z"/>
    <path d="M17.6 21.2 4.2 27.8l3.6 5.4 12-6z"/>
    <path d="M46.4 21.2 59.8 27.8l-3.6 5.4-12-6z"/>
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
  <text x="130" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="18" font-weight="700" fill="#ec941c">ABS</text>
  <text x="210" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="18" font-weight="700" fill="#e22820">BRAKE</text>
  <g transform="translate(268,16)" fill="#e22820">
    <rect x="6" y="2" width="6" height="4" rx="0.4"/>
    <rect x="16" y="2" width="6" height="4" rx="0.4"/>
    <path fill-rule="evenodd" d="M2 8h24v16H2z M4 10.4h20v11.2H4z"/>
    <rect x="6" y="15" width="6" height="2"/>
    <rect x="15" y="15" width="6" height="2"/>
    <rect x="17.2" y="12.4" width="1.8" height="7.2"/>
  </g>
  <g transform="translate(316,14)" fill="#e22820">
    <path d="M3 14h4.2c2.2 0 3.6 1.4 3.6 3.4S9.4 21 7.2 21H3z"/>
    <path fill-rule="evenodd" d="M10 11h12v16H10z M12.2 13.6h7.6v10.8h-7.6z"/>
    <path d="M22 11 34 4.2l2.4 2.6-8.2 6.6V27H22z"/>
    <path d="M32.4 10.2c0 2.6 1.8 4.6 3.4 4.6s3.4-2 3.4-4.6c0-2-1.6-3.8-3.4-5.6-1.8 1.8-3.4 3.6-3.4 5.6z"/>
  </g>
  <g transform="translate(360,14)" fill="#ec941c">
    <path d="M4 16h5l2.4-5.2h7l1.6 5.2h12l2.6-3.4H38v5.4h2.4v9H38V36H4v-4H1.2v-8.2H4z"/>
    <rect x="12" y="20" width="20" height="5.6" fill="#0a0a0a"/>
    <text x="22" y="25" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="6" font-weight="800" fill="#ec941c">CHECK</text>
  </g>
  <g transform="translate(414,16)" fill="#28c85c">
    <path fill-rule="evenodd" d="M10 6.2a8.4 8.4 0 1 0 .01 0zm0 4.2a4.2 4.2 0 1 0 .01 0z"/>
    <rect x="16" y="13" width="18" height="5.2" rx="0.5"/>
    <rect x="27" y="18" width="2.8" height="6"/>
    <rect x="31.6" y="18" width="2.8" height="8.2"/>
  </g>
  <text x="500" y="32" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#ec941c">MAINT</text>
  <text x="500" y="48" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#ec941c">REQ'D</text>
  <text x="568" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="16" font-weight="700" fill="#ec941c">EPS</text>
  <g transform="translate(600,10)" fill="#e22820">
    <circle cx="22" cy="8.6" r="5.5"/>
    <path fill-rule="evenodd" d="M11 18.4c0-2 3.2-3.6 11-3.6s11 1.6 11 3.6V40H11z M13.4 17.2 33.6 40h-7.4L12.2 22.4z"/>
  </g>
  <g transform="translate(652,8)" fill="#e22820">
    <path fill-rule="evenodd" d="M18.4 6h13.2l5.6 6.2v24.4L31.6 43H18.4l-5.6-6.4V12.2z M21.6 12h6.8v5H21.6z"/>
    <path d="M13 20 4.2 25.4l2.2 3.4 8.6-4.6z"/>
    <path d="M37 20l8.8 5.4-2.2 3.4-8.6-4.6z"/>
  </g>
  <text x="760" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="16" font-weight="700" fill="#e22820">SRS</text>
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
