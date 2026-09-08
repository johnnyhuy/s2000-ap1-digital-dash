#!/usr/bin/env python3
"""Rasterise white OEM telltale PNGs from the SVG plates (rsvg)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    script = ROOT / "scripts" / "rasterize_icons.py"
    raise SystemExit(subprocess.call([sys.executable, str(script)]))


if __name__ == "__main__":
    main()
