#!/usr/bin/env python3
"""Write original OEM-style telltale SVGs (white on transparent)."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets" / "icons"

HEADER = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" width="{vb_w}" height="{vb_h}" role="img" aria-label="{label}">
  <title>{label}</title>
'''
FOOT = "</svg>\n"


def wrap(name: str, body: str, vb_w: int = 64, vb_h: int = 48, label: str | None = None) -> str:
    return HEADER.format(vb_w=vb_w, vb_h=vb_h, label=label or name) + body + FOOT


SVGS: dict[str, str] = {
    "turn_l": wrap(
        "turn_l",
        '  <polygon fill="#fff" points="44,10 14,24 44,38"/>\n',
        label="Left turn telltale",
    ),
    "turn_r": wrap(
        "turn_r",
        '  <polygon fill="#fff" points="20,10 50,24 20,38"/>\n',
        label="Right turn telltale",
    ),
    "high_beam": wrap(
        "high_beam",
        """  <circle cx="24" cy="24" r="10" fill="none" stroke="#fff" stroke-width="2.4"/>
  <path d="M24 14a10 10 0 0 0 0 20" fill="none" stroke="#fff" stroke-width="2.4"/>
  <path d="M36 14l14-2M36 20l14-1M36 28l14 1M36 34l14 2" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
""",
        label="High beam telltale",
    ),
    "abs": wrap(
        "abs",
        '  <text x="32" y="31" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="16" font-weight="700" fill="#fff">ABS</text>\n',
        label="ABS telltale",
    ),
    "brake": wrap(
        "brake",
        '  <text x="48" y="31" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="15" font-weight="700" fill="#fff">BRAKE</text>\n',
        vb_w=96,
        label="BRAKE telltale",
    ),
    "battery": wrap(
        "battery",
        """  <rect x="16" y="16" width="32" height="20" rx="2" fill="none" stroke="#fff" stroke-width="2.4"/>
  <rect x="22" y="12" width="8" height="5" fill="#fff"/>
  <rect x="34" y="12" width="8" height="5" fill="#fff"/>
  <path d="M24 26h6M36 26h6M39 23v6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>
""",
        label="Battery telltale",
    ),
    "oil": wrap(
        "oil",
        """  <rect x="16" y="20" width="22" height="13" rx="2" fill="#fff"/>
  <path d="M36 20l12-8 3 3-10 8z" fill="#fff"/>
  <circle cx="18" cy="36" r="3.2" fill="#fff"/>
  <ellipse cx="18" cy="40" rx="2.4" ry="3" fill="#fff"/>
""",
        label="Oil pressure telltale",
    ),
    "cel": wrap(
        "cel",
        """  <rect x="12" y="16" width="40" height="18" rx="3" fill="none" stroke="#fff" stroke-width="2.3"/>
  <rect x="24" y="10" width="16" height="7" fill="none" stroke="#fff" stroke-width="2"/>
  <path d="M12 25l-7 5M52 25l7 5" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
  <text x="32" y="29" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="7" font-weight="700" fill="#fff">CHECK</text>
""",
        label="Check engine telltale",
    ),
    "immobilizer": wrap(
        "immobilizer",
        """  <circle cx="20" cy="24" r="9" fill="none" stroke="#fff" stroke-width="2.4"/>
  <circle cx="20" cy="24" r="3.2" fill="#fff"/>
  <rect x="28" y="21" width="22" height="6" rx="1" fill="#fff"/>
  <rect x="42" y="21" width="4" height="11" fill="#fff"/>
  <rect x="48" y="21" width="4" height="8" fill="#fff"/>
""",
        label="Immobilizer key telltale",
    ),
    "maint": wrap(
        "maint",
        """  <text x="32" y="22" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="11" font-weight="700" fill="#fff">MAINT</text>
  <text x="32" y="36" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="11" font-weight="700" fill="#fff">REQ'D</text>
""",
        label="MAINT REQ'D telltale",
    ),
    "eps": wrap(
        "eps",
        '  <text x="32" y="31" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="16" font-weight="700" fill="#fff">EPS</text>\n',
        label="EPS telltale",
    ),
    "seatbelt": wrap(
        "seatbelt",
        """  <circle cx="32" cy="12" r="6" fill="none" stroke="#fff" stroke-width="2.2"/>
  <path d="M22 40c2-12 6-16 10-16s8 4 10 16" fill="none" stroke="#fff" stroke-width="2.2"/>
  <path d="M20 38L42 16" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/>
""",
        label="Seatbelt telltale",
    ),
    "door": wrap(
        "door",
        """  <rect x="24" y="10" width="16" height="28" rx="5" fill="none" stroke="#fff" stroke-width="2.2"/>
  <rect x="27" y="6" width="10" height="5" rx="2" fill="none" stroke="#fff" stroke-width="2"/>
  <path d="M24 18l-10-5M24 28l-10-3M40 18l10-5M40 28l10-3" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/>
""",
        label="Door-open telltale",
    ),
    "srs": wrap(
        "srs",
        '  <text x="32" y="31" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="16" font-weight="700" fill="#fff">SRS</text>\n',
        label="SRS telltale",
    ),
}

ATLAS = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 72" width="980" height="72" role="img" aria-label="AP1 OEM lamp atlas">
  <title>AP1 OEM lamp atlas — self-test order</title>
  <rect width="980" height="72" fill="#0a0a0a"/>
  <!-- signal pair + self-test strip colours -->
  <g transform="translate(8,12)" fill="#2cc458"><polygon points="30,6 6,24 30,42"/></g>
  <g transform="translate(48,12)" stroke="#1c56d6" fill="none" stroke-width="2.4">
    <circle cx="16" cy="24" r="10"/><path d="M28 14l12-2M28 20l12-1M28 28l12 1M28 34l12 2"/>
  </g>
  <text x="130" y="44" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="18" font-weight="700" fill="#e48a1a">ABS</text>
  <text x="210" y="44" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="18" font-weight="700" fill="#d6221e">BRAKE</text>
  <g transform="translate(268,16)" stroke="#d6221e" fill="none" stroke-width="2.2">
    <rect x="4" y="10" width="28" height="16" rx="2"/><rect x="8" y="6" width="6" height="4" fill="#d6221e" stroke="none"/><rect x="20" y="6" width="6" height="4" fill="#d6221e" stroke="none"/>
  </g>
  <g transform="translate(316,16)" fill="#d6221e">
    <rect x="4" y="12" width="18" height="11" rx="2"/><path d="M20 12l10-6 2 2-8 6z"/><circle cx="6" cy="28" r="3"/>
  </g>
  <g transform="translate(360,14)" stroke="#e48a1a" fill="none" stroke-width="2">
    <rect x="2" y="10" width="36" height="16" rx="2"/><rect x="12" y="4" width="16" height="7"/>
    <text x="20" y="22" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="6" font-weight="700" fill="#e48a1a" stroke="none">CHECK</text>
  </g>
  <g transform="translate(412,16)" fill="none" stroke="#2cc458" stroke-width="2.2">
    <circle cx="12" cy="18" r="8"/><rect x="20" y="15" width="18" height="5" fill="#2cc458" stroke="none"/>
  </g>
  <text x="500" y="32" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="11" font-weight="700" fill="#e48a1a">MAINT</text>
  <text x="500" y="48" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="11" font-weight="700" fill="#e48a1a">REQ'D</text>
  <text x="568" y="44" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="16" font-weight="700" fill="#e48a1a">EPS</text>
  <g transform="translate(600,12)" fill="none" stroke="#d6221e" stroke-width="2.2">
    <circle cx="22" cy="10" r="5"/><path d="M12 38c2-12 6-16 10-16s8 4 10 16"/><path d="M10 36L32 14" stroke-width="3"/>
  </g>
  <g transform="translate(656,10)" fill="none" stroke="#d6221e" stroke-width="2.1">
    <rect x="16" y="8" width="14" height="28" rx="4"/><path d="M16 18l-9-4M16 28l-9-2M30 18l9-4M30 28l9-2"/>
  </g>
  <text x="760" y="44" text-anchor="middle" font-family="DejaVu Sans, Arial, sans-serif" font-size="16" font-weight="700" fill="#d6221e">SRS</text>
  <g transform="translate(800,12)" fill="#2cc458"><polygon points="14,6 44,24 14,42"/></g>
</svg>
'''


def main() -> None:
    DEST.mkdir(parents=True, exist_ok=True)
    for name, svg in SVGS.items():
        path = DEST / f"{name}.svg"
        path.write_text(svg, encoding="utf-8")
        print(path)
    atlas = DEST / "atlas.svg"
    atlas.write_text(ATLAS, encoding="utf-8")
    print(atlas)


if __name__ == "__main__":
    main()
