#!/usr/bin/env python3
"""Phase 1 fullscreen gauge UI — reads Telemetry JSON lines from stdin.

Pipe from the mock:
  python src/mock_telemetry.py | python src/gauge_ui.py
"""
from __future__ import annotations

import math
import select
import sys
from pathlib import Path

import pygame

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocol import (
    BATT_LOW_V,
    ECT_HOT_C,
    FUEL_LOW_PCT,
    RPM_REDLINE,
    SPEED_MAX_KMH,
    Telemetry,
    try_parse_line,
)

W, H = 1920, 1080
BG = (8, 10, 14)
FG = (230, 235, 240)
ACCENT = (0, 180, 255)
WARN = (255, 70, 70)
GOOD = (40, 200, 120)


def drain_stdin(current: Telemetry) -> Telemetry:
    """Non-blocking: consume all ready JSON lines; keep the latest."""
    latest = current
    while True:
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if not ready:
            break
        line = sys.stdin.readline()
        if not line:
            break
        parsed = try_parse_line(line)
        if parsed is not None:
            latest = parsed
    return latest


def draw_arc_gauge(
    surf: pygame.Surface,
    cx: int,
    cy: int,
    r: int,
    value: float,
    vmax: float,
    label: str,
    unit: str,
) -> None:
    pygame.draw.circle(surf, (30, 34, 42), (cx, cy), r, 3)
    start = math.radians(135)
    span = math.radians(270)
    frac = max(0.0, min(1.0, value / vmax))
    steps = max(2, int(80 * frac))
    pts = [(cx, cy)]
    for i in range(steps + 1):
        a = start + span * (i / 80) * frac
        pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
    if len(pts) > 2:
        pygame.draw.polygon(surf, ACCENT, pts)
        pygame.draw.circle(surf, BG, (cx, cy), r - 28)
    font_b = pygame.font.SysFont("DejaVu Sans", 64, bold=True)
    font_s = pygame.font.SysFont("DejaVu Sans", 28)
    text = font_b.render(f"{int(value)}", True, FG)
    surf.blit(text, text.get_rect(center=(cx, cy - 10)))
    sub = font_s.render(f"{label} {unit}".strip(), True, (140, 150, 160))
    surf.blit(sub, sub.get_rect(center=(cx, cy + 40)))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
    pygame.display.set_caption("S2000 Phase 1")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("DejaVu Sans", 36)
    font_sm = pygame.font.SysFont("DejaVu Sans", 24)

    telem = Telemetry()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

        telem = drain_stdin(telem)
        screen.fill(BG)

        draw_arc_gauge(screen, 480, 520, 220, telem.rpm, RPM_REDLINE, "RPM", "")
        draw_arc_gauge(
            screen, 1440, 520, 220, telem.speed_kmh, SPEED_MAX_KMH, "SPEED", "km/h"
        )

        oil_ok = not telem.lamp("oil")
        rows = [
            ("FUEL", f"{telem.fuel_pct:.0f}%", GOOD if telem.fuel_pct > FUEL_LOW_PCT else WARN),
            ("ECT", f"{telem.ect_c:.0f}°C", GOOD if telem.ect_c < ECT_HOT_C else WARN),
            ("BATT", f"{telem.batt_v:.1f}V", GOOD if telem.batt_v > BATT_LOW_V else WARN),
            ("ODO", f"{telem.odo_km:.1f} km", FG),
            ("OIL", "OK" if oil_ok else "LOW", GOOD if oil_ok else WARN),
        ]
        y = 120
        for name, val, col in rows:
            screen.blit(font_sm.render(name, True, (120, 130, 140)), (60, y))
            screen.blit(font.render(val, True, col), (60, y + 28))
            y += 100

        title = font_sm.render("AP1 PHASE 1 — MOCK JSON", True, (90, 100, 110))
        screen.blit(title, (W // 2 - title.get_width() // 2, 40))

        if telem.lamp("turn_l"):
            pygame.draw.polygon(screen, GOOD, [(80, 80), (120, 60), (120, 100)])
        if telem.lamp("turn_r"):
            pygame.draw.polygon(screen, GOOD, [(W - 80, 80), (W - 120, 60), (W - 120, 100)])
        if telem.lamp("high_beam"):
            screen.blit(font_sm.render("HIGH BEAM", True, ACCENT), (W // 2 - 60, 80))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
