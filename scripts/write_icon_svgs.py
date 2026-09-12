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
    <rect x="17.4" y="5.2" width="10.4" height="7.2" rx="0.8"/>
    <rect x="36.2" y="5.2" width="10.4" height="7.2" rx="0.8"/>
    <path fill-rule="evenodd" d="M8.8 12.8h46.4v30.4H8.8z M15.6 19.2h32.8v17.6H15.6z"/>
    <rect x="18.6" y="25.6" width="11.6" height="3.4"/>
    <rect x="22.7" y="21.4" width="3.4" height="11.8"/>
    <rect x="34.2" y="25.6" width="11.6" height="3.4"/>
  </g>
""",
        label="Battery telltale",
    ),
    "oil": wrap(
        "oil",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M3.2 26.4c0-9.2 6.6-16 16.6-16h6.4v5.2H20.2c-5.8 0-9.6 4-9.6 10.8s3.8 10.8 9.6 10.8h6v5.2h-6.4C9.8 42.4 3.2 35.6 3.2 26.4z"/>
    <rect x="27.8" y="11.2" width="11.4" height="5" rx="0.7"/>
    <path fill-rule="evenodd" d="M19.6 16h26.6v22.4H19.6z M24.4 20.8h17v12.8H24.4z"/>
    <path fill-rule="evenodd" d="M44.6 16.2 55.8 6.2l5.2 5.4-8.6 8z M48.2 17.8 56.2 10.4l1.8 1.9-6.4 5.8z"/>
    <path d="M57.6 14.6c0 3.2 2.2 5.6 4.2 5.6s4.2-2.4 4.2-5.6c0-2.4-1.8-5.4-4.2-8.4-2.4 3-4.2 6-4.2 8.4z"/>
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
    <path fill-rule="evenodd" d="M17.2 5.6a16.6 16.6 0 1 0 .02 0zm0 7.4a9.2 9.2 0 1 0 .02 0z"/>
    <rect x="30.4" y="19.2" width="30.6" height="8.4" rx="1.5"/>
    <rect x="48.2" y="27.4" width="5.4" height="9.6" rx="0.8"/>
    <rect x="55.8" y="27.4" width="5.4" height="13.4" rx="0.8"/>
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
    <circle cx="32" cy="8.2" r="6.5"/>
    <path d="M29.2 13.8h5.6v3.4h-5.6z"/>
    <path fill-rule="evenodd" d="M16.8 17.6 24.6 16.2 28 19h8l3.4-2.8 7.8 1.4-2.6 27.8H19.4z M20.4 15.2 49.6 45.4h-14L18.4 21.6z"/>
    <path d="M21.6 15.4 47.4 45h-8.8L20.2 22.2z"/>
  </g>
""",
        label="Seatbelt telltale",
    ),
    "door": wrap(
        "door",
        """  <g fill="#fff">
    <path fill-rule="evenodd" d="M25.4 2.2h13.2c2 0 3.8 1.15 4.7 2.95L47.4 11.4v26.4c0 1.7-1 3.3-2.6 4.3L38.2 46H25.8l-6.6-3.9c-1.6-1-2.6-2.6-2.6-4.3V11.4L20.7 5.15C21.6 3.35 23.4 2.2 25.4 2.2z M27.6 8.6h8.8v8.4h-8.8z"/>
    <path d="M18.2 20.6 2.8 28.6l3.6 6 13.6-7.2z"/>
    <path d="M45.8 20.6 61.2 28.6l-3.6 6-13.6-7.2z"/>
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
    <rect x="5.4" y="1.4" width="6.4" height="4.4" rx="0.4"/>
    <rect x="16.2" y="1.4" width="6.4" height="4.4" rx="0.4"/>
    <path fill-rule="evenodd" d="M1.4 7.6h25.2v17.2H1.4z M4.8 11h18.4v10.4H4.8z"/>
    <rect x="6.2" y="14.8" width="6.4" height="2"/>
    <rect x="8.4" y="12.6" width="2" height="6.4"/>
    <rect x="15.4" y="14.8" width="6.4" height="2"/>
  </g>
  <g transform="translate(316,14)" fill="#e22820">
    <path fill-rule="evenodd" d="M1.6 18.8c0-5.6 4-9.6 10-9.6h4.6v3.4h-4c-3.2 0-5.4 2.2-5.4 6.2s2.2 6.2 5.4 6.2h4V28h-4.6c-6 0-10-4-10-9.2z"/>
    <rect x="13" y="11.6" width="16.4" height="13.6" rx="0.8"/>
    <path d="M28.4 11.6 37.6 4.2l3.4 3.6-6.4 5.6z"/>
    <path d="M38.6 11.2c0 2.4 1.6 4.2 3.2 4.2s3.2-1.8 3.2-4.2c0-1.8-1.4-4-3.2-6.2-1.8 2.2-3.2 4.4-3.2 6.2z"/>
  </g>
  <g transform="translate(360,14)" fill="#ec941c">
    <path d="M4 16h5l2.4-5.2h7l1.6 5.2h12l2.6-3.4H38v5.4h2.4v9H38V36H4v-4H1.2v-8.2H4z"/>
    <rect x="12" y="20" width="20" height="5.6" fill="#0a0a0a"/>
    <text x="22" y="25" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="6" font-weight="800" fill="#ec941c">CHECK</text>
  </g>
  <g transform="translate(414,16)" fill="#28c85c">
    <path fill-rule="evenodd" d="M9.4 4.4a10.2 10.2 0 1 0 .01 0zm0 4.6a5.6 5.6 0 1 0 .01 0z"/>
    <rect x="17.2" y="12.4" width="19.2" height="5.6" rx="0.7"/>
    <rect x="28.4" y="18" width="3.2" height="6.4"/>
    <rect x="33.2" y="18" width="3.2" height="8.8"/>
  </g>
  <text x="500" y="32" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#ec941c">MAINT</text>
  <text x="500" y="48" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#ec941c">REQ'D</text>
  <text x="568" y="44" text-anchor="middle" font-family="Barlow Condensed, DejaVu Sans, Liberation Sans, sans-serif" font-size="16" font-weight="700" fill="#ec941c">EPS</text>
  <g transform="translate(600,10)" fill="#e22820">
    <circle cx="22" cy="8" r="5.6"/>
    <path d="M19.6 13h4.8v2.8h-4.8z"/>
    <path fill-rule="evenodd" d="M10.4 17.4 16.8 16.2 19.4 18.4h5.2l2.6-2.2 6.4 1.2-2.2 22.2H12.6z M14.8 16.6 34.8 39.6h-6.4L13.2 21.6z"/>
    <path d="M14.2 16 33.8 39.2h-4.8L13.2 21.2z"/>
  </g>
  <g transform="translate(652,8)" fill="#e22820">
    <path fill-rule="evenodd" d="M17.6 5.2h13.6c1.6 0 3.1 .9 3.8 2.4L39.2 13.6v21.6c0 1.4-.8 2.7-2.1 3.5L32 42.4H20l-5.1-3.7c-1.3-.8-2.1-2.1-2.1-3.5V13.6L13.8 7.6c.7-1.5 2.2-2.4 3.8-2.4z M21.2 12.2h6.4v5.8h-6.4z"/>
    <path d="M12.8 18.4 3.2 23.6l2.4 4 8.8-4.8z"/>
    <path d="M39.2 18.4l9.6 5.2-2.4 4-8.8-4.8z"/>
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
