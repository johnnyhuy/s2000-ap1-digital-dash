#!/usr/bin/env python3
"""Write 32×32 OEM-style lamp pictograms into assets/icons/."""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gauge_ui import (  # noqa: E402
    LAMP_AMBER,
    LAMP_BLUE,
    LAMP_GREEN,
    LAMP_RED,
    _draw_lamp_icon,
    init_pygame,
)


ICONS = (
    ("turn_l", LAMP_GREEN),
    ("turn_r", LAMP_GREEN),
    ("key", LAMP_GREEN),
    ("hi", LAMP_BLUE),
    ("oil", LAMP_RED),
    ("bat", LAMP_RED),
    ("brake", LAMP_RED),
    ("srs", LAMP_RED),
    ("seat", LAMP_RED),
    ("door", LAMP_RED),
    ("cel", LAMP_AMBER),
    ("eps", LAMP_AMBER),
    ("abs", LAMP_AMBER),
    ("maint", LAMP_AMBER),
)


def main() -> None:
    dest = Path(__file__).resolve().parents[1] / "assets" / "icons"
    dest.mkdir(parents=True, exist_ok=True)
    pygame, _screen = init_pygame(True, True)
    for kind, col in ICONS:
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        _draw_lamp_icon(pygame, surf, kind, 16, 16, col)
        path = dest / f"{kind}.png"
        pygame.image.save(surf, str(path))
        print(path)
    pygame.quit()


if __name__ == "__main__":
    main()
