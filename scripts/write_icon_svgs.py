#!/usr/bin/env python3
"""Write AP1 telltale SVGs traced from OEM lamp-strip / self-test plates.

Source of truth is the OEM silhouettes (ISO 2575 wording + Honda AP1
pictograms), not crude boxes. Rasterise with ``scripts/rasterize_icons.py``.

Plates live in ``refs/oem/plates/`` (atlas + pictogram close-ups generated
from the Car Spy AP1 frame and the self-test lamp-strip descriptions).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "icons"

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
        '  <path fill="#fff" d="M44 8 8 24l36 16v-9h14V17H44z"/>\n',
        label="Left turn telltale",
    ),
    "turn_r": wrap(
        "turn_r",
        '  <path fill="#fff" d="M20 8v9H6v14h14v9l36-16z"/>\n',
        label="Right turn telltale",
    ),
    "high_beam": wrap(
        "high_beam",
        """  <path fill="#fff" d="M38 10c12 0 18.5 8.2 18.5 14S50 38 38 38h-6V10h6z"/>
  <path stroke="#fff" stroke-width="2.6" stroke-linecap="square" fill="none"
        d="M6 14.5h24M4 19.5h26M4 24.5h26M4 29.5h26M6 34.5h24"/>
""",
        label="High beam telltale",
    ),
    "abs": wrap(
        "abs",
        WORD.format(x=32, y=31, size=16, track="0.6", label="ABS"),
        label="ABS telltale",
    ),
    "brake": wrap(
        "brake",
        WORD.format(x=48, y=31, size=15, track="0.8", label="BRAKE"),
        vb_w=96,
        label="BRAKE telltale",
    ),
    "battery": wrap(
        "battery",
        """  <defs>
    <mask id="batt">
      <rect width="64" height="48" fill="black"/>
      <rect x="14" y="16" width="36" height="22" rx="1.2" fill="white"/>
      <rect x="20" y="11" width="8" height="6" rx="0.4" fill="white"/>
      <rect x="36" y="11" width="8" height="6" rx="0.4" fill="white"/>
      <rect x="19" y="25.2" width="9" height="2.8" fill="black"/>
      <rect x="36" y="25.2" width="9" height="2.8" fill="black"/>
      <rect x="39.1" y="21.2" width="2.8" height="10.8" fill="black"/>
    </mask>
  </defs>
  <rect width="64" height="48" fill="#fff" mask="url(#batt)"/>
""",
        label="Battery telltale",
    ),
    "oil": wrap(
        "oil",
        """  <path fill="#fff" d="M10 22.5c0-2.8 2-5 5.2-5H18v16H12.4C10.8 33.5 10 31.6 10 29.2z"/>
  <path fill="#fff" d="M18 20h16.5v18H18z"/>
  <path fill="#fff" d="M34.5 20 51 7.2l3.6 3.4-11.2 9.2V38h-9z"/>
  <path fill="#fff" d="M50.2 15.4c0 3.8 2.8 6.8 5.2 6.8s5.2-3 5.2-6.8c0-3-2.4-5.6-5.2-8.4-2.8 2.8-5.2 5.4-5.2 8.4z"/>
""",
        label="Oil pressure telltale",
    ),
    "cel": wrap(
        "cel",
        """  <path fill="#fff" d="M9 20.5h7.2l3.2-7.6h13.2l2.2 7.6H52l4.2-4.8h4.8v7.2h2.6v12.6h-2.6v7.6H9v-7.6H4.2V28.2H9z"/>
  <path fill="#0a0a0a" d="M17.6 26.6h28.8v5.6H17.6z"/>
  <path fill="#fff" d="M20 28h3.4v3H20zm5.4 0h3.4v3h-3.4zm5.4 0h3.4v3h-3.4zm5.4 0h3.4v3h-3.4zm5.4 0h3.4v3h-3.4z"/>
""",
        label="Check engine telltale",
    ),
    "immobilizer": wrap(
        "immobilizer",
        """  <defs>
    <mask id="key">
      <rect width="64" height="48" fill="black"/>
      <circle cx="18" cy="24" r="10" fill="white"/>
      <rect x="26" y="20.8" width="26" height="6.4" fill="white"/>
      <rect x="41.2" y="27" width="3.6" height="7.2" fill="white"/>
      <rect x="47.2" y="27" width="3.6" height="10" fill="white"/>
      <circle cx="18" cy="24" r="4" fill="black"/>
    </mask>
  </defs>
  <rect width="64" height="48" fill="#fff" mask="url(#key)"/>
""",
        label="Immobilizer key telltale",
    ),
    "maint": wrap(
        "maint",
        WORD.format(x=32, y=21, size=12.5, track="0.2", label="MAINT")
        + WORD.format(x=32, y=36, size=12.5, track="0.05", label="REQ'D"),
        label="MAINT REQ'D telltale",
    ),
    "eps": wrap(
        "eps",
        WORD.format(x=32, y=31, size=16, track="0.6", label="EPS"),
        label="EPS telltale",
    ),
    "seatbelt": wrap(
        "seatbelt",
        """  <circle cx="32" cy="10" r="6.6" fill="#fff"/>
  <path fill="#fff" d="M18 20.4c0-2.4 4.2-4.6 14-4.6s14 2.2 14 4.6V42H18z"/>
  <path fill="#0a0a0a" d="M21.2 19 44 42h-8.4L19.6 24.2z"/>
""",
        label="Seatbelt telltale",
    ),
    "door": wrap(
        "door",
        """  <path fill="#fff" d="M23.5 5.5h17l7.2 7.4v27.2L40.5 48h-17L16.3 40.1V12.9z"/>
  <rect x="27.2" y="11" width="9.4" height="6.2" rx="0.7" fill="#0a0a0a"/>
  <path fill="#fff" d="M16.4 21 3.4 27.4l3.2 4.8 12.6-5.8z"/>
  <path fill="#fff" d="M47.6 21 60.6 27.4l-3.2 4.8-12.6-5.8z"/>
""",
        label="Door-open telltale",
    ),
    "srs": wrap(
        "srs",
        WORD.format(x=32, y=31, size=16, track="0.6", label="SRS"),
        label="SRS telltale",
    ),
}

ATLAS = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 72" width="980" height="72" role="img" aria-label="AP1 OEM lamp atlas">
  <title>AP1 OEM lamp atlas — self-test order</title>
  <rect width="980" height="72" fill="#0a0a0a"/>
  <g transform="translate(8,16)" fill="#2cc458"><path d="M34 6 6 24l28 18v-10h10V16H34z"/></g>
  <g transform="translate(52,16)" fill="#1c56d6">
    <path d="M28 8c9 0 14 6.4 14 10.4S37 28.8 28 28.8h-4V8h4z"/>
    <path d="M4 11h18M2 15.2h20M2 19.2h20M2 23.2h20M4 27.2h18" stroke="#1c56d6" stroke-width="2" fill="none"/>
  </g>
  <text x="130" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="18" font-weight="700" fill="#e48a1a">ABS</text>
  <text x="210" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="18" font-weight="700" fill="#d6221e">BRAKE</text>
  <g transform="translate(268,18)" fill="#d6221e">
    <rect x="4" y="8" width="30" height="16" rx="1"/>
    <rect x="8" y="4" width="6" height="5"/>
    <rect x="22" y="4" width="6" height="5"/>
    <rect x="8" y="14" width="7" height="2.2" fill="#0a0a0a"/>
    <rect x="22" y="14" width="7" height="2.2" fill="#0a0a0a"/>
    <rect x="24.4" y="11" width="2.2" height="8.2" fill="#0a0a0a"/>
  </g>
  <g transform="translate(316,16)" fill="#d6221e">
    <path d="M4 12h16l8-7 2.4 2.6-6 5.4V28H4z"/>
    <path d="M28 10c0 2.4 1.8 4.4 3.2 4.4s3.2-2 3.2-4.4c0-1.8-1.4-3.4-3.2-5-1.8 1.6-3.2 3.2-3.2 5z"/>
  </g>
  <g transform="translate(360,14)" fill="#e48a1a">
    <path d="M4 16h5l2.4-5.2h7l1.6 5.2h12l2.6-3.4H38v5.4h2.4v9H38V36H4v-4H1.2v-8.2H4z"/>
    <text x="20" y="26" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="6" font-weight="800" fill="#0a0a0a">CHECK</text>
  </g>
  <g transform="translate(414,18)" fill="#2cc458">
    <circle cx="10" cy="16" r="8"/>
    <circle cx="10" cy="16" r="3.2" fill="#0a0a0a"/>
    <rect x="16" y="13.2" width="18" height="5.4"/>
    <rect x="27" y="18.4" width="2.8" height="6"/>
    <rect x="31.4" y="18.4" width="2.8" height="8"/>
  </g>
  <text x="500" y="32" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#e48a1a">MAINT</text>
  <text x="500" y="48" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="11" font-weight="700" fill="#e48a1a">REQ'D</text>
  <text x="568" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="16" font-weight="700" fill="#e48a1a">EPS</text>
  <g transform="translate(600,12)" fill="#d6221e">
    <circle cx="22" cy="10" r="5.4"/>
    <path d="M12 20c0-2 3-3.4 10-3.4s10 1.4 10 3.4v14H12z"/>
    <path d="M15 18 32 40h-6.4L14 24z" fill="#0a0a0a"/>
  </g>
  <g transform="translate(652,10)" fill="#d6221e">
    <path d="M20 8h12l5 6v22l-5 6H20l-5-6V14z"/>
    <path d="M15 20 6 25.2l1.8 3.2 9-4.4z"/>
    <path d="M37 20l9 5.2-1.8 3.2-9-4.4z"/>
  </g>
  <text x="760" y="44" text-anchor="middle" font-family="DejaVu Sans, Liberation Sans, sans-serif" font-size="16" font-weight="700" fill="#d6221e">SRS</text>
  <g transform="translate(800,16)" fill="#2cc458"><path d="M10 6v9H0v12h10v9l28-15z"/></g>
</svg>
'''


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, svg in SVGS.items():
        path = DEST / f"{name}.svg"
        path.write_text(svg, encoding="utf-8")
        print(path.relative_to(ROOT))
    atlas = DEST / "atlas.svg"
    atlas.write_text(ATLAS, encoding="utf-8")
    print(atlas.relative_to(ROOT))


if __name__ == "__main__":
    main()
