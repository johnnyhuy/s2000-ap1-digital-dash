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


# CHECK letter holes for the CEL block (single outlines so evenodd punches).
CHECK_HOLES = (
    "M16.2 22.2h5.1v2.05h-3.05v4.5h3.05v2.05h-5.1z"
    "M22.2 22.2h2.05v3.35h1.7V22.2h2.05v8.6h-2.05v-3.2h-1.7v3.2H22.2z"
    "M29.1 22.2h5.05v2.05h-3v1.55h2.45v1.9H31.15v1.05h3v2.05h-5.05z"
    "M35.3 22.2h5.1v2.05h-3.05v4.5h3.05v2.05h-5.1z"
    "M41.5 22.2h2.1v3.15l2.55-3.15h2.35L45.3 26.4l3.35 4.4h-2.45l-2.05-2.7v2.7h-2.1z"
)

SVGS: dict[str, str] = {
    "turn_l": wrap(
        "turn_l",
        '  <path fill="#fff" d="M44 9.2 7.2 24 44 38.8v-7.6h12.4V16.8H44z"/>\n',
        label="Left turn telltale",
    ),
    "turn_r": wrap(
        "turn_r",
        '  <path fill="#fff" d="M20 9.2v7.6H7.6v14.4H20v7.6L56.8 24z"/>\n',
        label="Right turn telltale",
    ),
    "high_beam": wrap(
        "high_beam",
        """  <g fill="#fff">
    <rect x="4.2" y="13.2" width="22.6" height="3.7" rx="0.4"/>
    <rect x="3.2" y="22.15" width="24.4" height="3.7" rx="0.4"/>
    <rect x="4.2" y="31.1" width="22.6" height="3.7" rx="0.4"/>
    <path fill-rule="evenodd" d="M33.6 8.2h6.4C54.8 8.2 61 15.4 61 24s-6.2 15.8-21 15.8h-6.4V8.2z M37.6 12.4v23.2h3.2c11.2 0 16-5.6 16-11.6S52 12.4 40.8 12.4h-3.2z"/>
  </g>
""",
        label="High beam telltale",
    ),
    "abs": wrap(
        "abs",
        WORD.format(x=32, y=31.2, size=18, track="0.9", label="ABS"),
        label="ABS telltale",
    ),
    "brake": wrap(
        "brake",
        WORD.format(x=48, y=31.2, size=17.2, track="1.15", label="BRAKE"),
        vb_w=96,
        label="BRAKE telltale",
    ),
    "battery": wrap(
        "battery",
        """  <g fill="#fff">
    <rect x="18.6" y="6.4" width="9.6" height="6.4" rx="0.7"/>
    <rect x="35.8" y="6.4" width="9.6" height="6.4" rx="0.7"/>
    <path fill-rule="evenodd" d="M10.4 13.2h43.2v28.4H10.4z M15.2 17.8h33.6v19.2H15.2z"/>
    <rect x="19.4" y="25.4" width="10.8" height="3.1"/>
    <rect x="23.25" y="21.5" width="3.1" height="10.9"/>
    <rect x="34.2" y="25.4" width="10.8" height="3.1"/>
  </g>
""",
        label="Battery telltale",
    ),
    "oil": wrap(
        "oil",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M4.2 25.2c0-8.4 6.2-14.6 15.2-14.6h6.2v4.6h-5.4c-5.2 0-8.6 3.6-8.6 10s3.4 10 8.6 10h5.4v4.6h-6.2C10.4 39.8 4.2 33.6 4.2 25.2z"/>
    <rect x="28.4" y="10.6" width="10.2" height="4.4" rx="0.6"/>
    <path fill-rule="evenodd" d="M20.8 14.8h24.8v21.2H20.8z M25.2 19.2h16v12.4H25.2z"/>
    <path fill-rule="evenodd" d="M45.4 14.8 56.4 4.6l4.6 5-8.8 8.2z M48.6 16.4 56.2 9.4l1.6 1.8-6.4 5.6z"/>
    <path d="M58.4 5.2c0 3.4 2.4 5.8 4.4 5.8s4.4-2.4 4.4-5.8c0-2.6-2-5.6-4.4-8.6-2.4 3-4.4 6-4.4 8.6z"/>
  </g>
""",
        label="Oil pressure telltale",
    ),
    "cel": wrap(
        "cel",
        f"""  <g fill="#fff">
    <path fill-rule="evenodd" d="M16.8 9.2h18.8c1.6 0 3 1.05 3.5 2.55l1.9 5.35h8.6l4.6-4.9h4.6v6.6h3.1v12.2h-3.1v6.8H8.4v-6.8H2.8V26.1h5.2v-4.2h6.6L15.4 11.7c.5-1.5 1.9-2.5 3.4-2.5z {CHECK_HOLES}"/>
  </g>
""",
        label="Check engine telltale",
    ),
    "immobilizer": wrap(
        "immobilizer",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M18.4 7.4a13.6 13.6 0 1 0 .02 0zm0 6.2a7.4 7.4 0 1 0 .02 0z"/>
    <rect x="29.2" y="20.4" width="28.8" height="6.6" rx="1.2"/>
    <rect x="45.6" y="27" width="4.4" height="8.4" rx="0.7"/>
    <rect x="52.4" y="27" width="4.4" height="11.8" rx="0.7"/>
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
    <circle cx="32" cy="8.4" r="6.6"/>
    <path fill-rule="evenodd" d="M18.4 16.6c0-2.4 6.1-4.8 13.6-4.8s13.6 2.4 13.6 4.8V45.4H18.4z M21.8 16 46.6 45.4h-8.8L20 22.6z"/>
  </g>
""",
        label="Seatbelt telltale",
    ),
    "door": wrap(
        "door",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M26.4 2.4h11.2c1.7 0 3.3 1 4.2 2.5L45.8 11.2v26.6c0 1.6-.9 3.1-2.3 4l-6.2 4.4H26.7l-6.2-4.4c-1.4-.9-2.3-2.4-2.3-4V11.2L22.2 4.9c.9-1.5 2.5-2.5 4.2-2.5z M29.6 9.6h4.8v7.2h-4.8z"/>
    <path d="M18.2 20.2 4.4 27.6l2.8 5.2 12.4-6.6z"/>
    <path d="M45.8 20.2 59.6 27.6l-2.8 5.2-12.4-6.6z"/>
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
    <path fill-rule="evenodd" d="M24 7.2h4.6C38.2 7.2 43 12.6 43 18.4S38.2 29.6 28.6 29.6H24V7.2z M26.8 10.2v16.4h2.2c7.6 0 10.8-3.8 10.8-8.2S36.6 10.2 29 10.2h-2.2z"/>
    <rect x="3.2" y="11.2" width="16.4" height="2.6" rx="0.3"/>
    <rect x="2.4" y="17.1" width="17.6" height="2.6" rx="0.3"/>
    <rect x="3.2" y="23" width="16.4" height="2.6" rx="0.3"/>
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
