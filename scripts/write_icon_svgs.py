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
        '  <path fill="#fff" d="M46 9 11 24l35 15v-9h12V18H46z"/>\n',
        label="Left turn telltale",
    ),
    "turn_r": wrap(
        "turn_r",
        '  <path fill="#fff" d="M18 9v9H6v12h12v9l35-15z"/>\n',
        label="Right turn telltale",
    ),
    "high_beam": wrap(
        "high_beam",
        """  <path fill="#fff" d="M36 11c11.5 0 18 8 18 13s-6.5 13-18 13h-5V11h5z"/>
  <path stroke="#fff" stroke-width="2.5" stroke-linecap="square" fill="none"
        d="M8 15h22M6 20h24M6 24.5h24M6 29h24M8 34h22"/>
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
        """  <path fill="#fff" d="M12 22h22c1.4 0 3.2-1.1 7.2-6.2L48 9.6l3.2 3.4-6.6 7.2V36H12V22z"/>
  <path fill="#fff" d="M10 24c0-3.2 1.6-5.2 4.2-5.2H16v8h-4.4C10.4 26.8 10 25.6 10 24z"/>
  <path fill="#fff" d="M46.2 16.4c0 3.4 2.5 6.2 4.6 6.2s4.6-2.8 4.6-6.2c0-2.6-2-4.8-4.6-7.2-2.6 2.4-4.6 4.6-4.6 7.2z"/>
""",
        label="Oil pressure telltale",
    ),
    "cel": wrap(
        "cel",
        """  <defs>
    <mask id="cel">
      <rect width="64" height="48" fill="black"/>
      <path fill="white" d="M12 22h6l3.2-7h9.2l2.2 7h15.2l3.6-4.6H58v7.4h3.4v12.2H58V40H12v-5.2H7.2V25.6H12z"/>
      <rect x="7" y="28" width="6" height="7" fill="white"/>
      <text x="32" y="33.4" text-anchor="middle" fill="black"
            font-family="DejaVu Sans, Liberation Sans, Arial Narrow, sans-serif"
            font-size="7.2" font-weight="800" letter-spacing="0.55">CHECK</text>
    </mask>
  </defs>
  <rect width="64" height="48" fill="#fff" mask="url(#cel)"/>
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
        WORD.format(x=32, y=22, size=11, track="0.35", label="MAINT")
        + WORD.format(x=32, y=36, size=11, track="0.15", label="REQ'D"),
        label="MAINT REQ'D telltale",
    ),
    "eps": wrap(
        "eps",
        WORD.format(x=32, y=31, size=16, track="0.6", label="EPS"),
        label="EPS telltale",
    ),
    "seatbelt": wrap(
        "seatbelt",
        """  <defs>
    <mask id="belt">
      <rect width="64" height="48" fill="black"/>
      <circle cx="32" cy="11.5" r="6.4" fill="white"/>
      <path fill="white" d="M20 20c0-2.2 3.6-4 12-4s12 1.8 12 4v7H20z"/>
      <path fill="white" d="M19 27h26v16H19z"/>
      <path fill="black" d="M22 20 42 42h-8L20 26z"/>
    </mask>
  </defs>
  <rect width="64" height="48" fill="#fff" mask="url(#belt)"/>
""",
        label="Seatbelt telltale",
    ),
    "door": wrap(
        "door",
        """  <path fill="#fff" d="M25 7h14l6.4 7.2v25.6L39 47H25l-6.4-7.2V14.2z"/>
  <rect x="28.4" y="11" width="7.2" height="5.2" fill="#000"/>
  <path fill="#fff" d="M18.6 20.4 7.2 26.2l2.4 4.2 11.2-5.4z"/>
  <path fill="#fff" d="M45.4 20.4 56.8 26.2l-2.4 4.2-11.2-5.4z"/>
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
