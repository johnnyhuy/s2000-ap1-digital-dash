#!/usr/bin/env python3
"""Rasterise white OEM telltale PNGs next to the SVG sources."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame

    from oem_icons import ASSETS, export_pngs

    pygame.init()
    pygame.display.set_mode((128, 128))
    written = export_pngs(pygame, ASSETS)
    for path in written:
        print(path, path.stat().st_size)
    pygame.quit()


if __name__ == "__main__":
    main()
