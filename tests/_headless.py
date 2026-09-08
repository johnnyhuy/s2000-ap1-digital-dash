"""Dummy-SDL helpers for headless cluster tests. Not collected by unittest."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(ROOT / "tests"))


def init_cluster():
    """Return (pygame, screen, fonts) on a dummy 1920×1080 surface."""
    from gauge_ui import W, H, build_fonts

    import pygame

    pygame.init()
    pygame.display.set_mode((64, 64))
    screen = pygame.Surface((W, H))
    return pygame, screen, build_fonts(pygame)


def sample_near(surf, target: tuple[int, int, int], *, step: int = 8, tol: int = 36) -> int:
    """Count grid samples whose RGB is within ``tol`` of ``target``."""
    w, h = surf.get_size()
    hits = 0
    tr, tg, tb = target
    for y in range(0, h, step):
        for x in range(0, w, step):
            px = surf.get_at((x, y))
            if px.a < 16:
                continue
            if abs(px.r - tr) <= tol and abs(px.g - tg) <= tol and abs(px.b - tb) <= tol:
                hits += 1
    return hits


def count_warm(surf, *, step: int = 8, min_r: int = 36) -> int:
    """Count amber-ish LCD samples (R high, B low) — sweep ghosts through live bloom."""
    w, h = surf.get_size()
    hits = 0
    for y in range(0, h, step):
        for x in range(0, w, step):
            px = surf.get_at((x, y))
            if px.a < 16:
                continue
            if px.r >= min_r and px.r > px.b and px.g >= px.b:
                hits += 1
    return hits


def region(surf, rect: tuple[int, int, int, int]):
    x, y, w, h = rect
    return surf.subsurface((x, y, w, h)).copy()
