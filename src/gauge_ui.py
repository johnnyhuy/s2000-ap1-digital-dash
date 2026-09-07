#!/usr/bin/env python3
"""Phase 1 fullscreen gauge UI — AP1-ish digital cluster.

Reads Telemetry JSON lines from stdin (or --serial in Phase 2).

  python mock_telemetry.py | python gauge_ui.py
  python gauge_ui.py --windowed
  python gauge_ui.py --smoke

Esc or Q quits.
"""
from __future__ import annotations

import argparse
import math
import os
import select
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocol import (
    BATT_LOW_V,
    ECT_HOT_C,
    FUEL_LOW_PCT,
    RPM_REDLINE,
    RPM_VTEC,
    SPEED_MAX_KMH,
    SERIAL_BAUD,
    Telemetry,
    try_parse_line,
)

W, H = 1920, 1080

# Dark cluster, AP1 yellow tach DNA
BG = (6, 8, 12)
PANEL = (14, 18, 26)
PANEL_EDGE = (32, 38, 50)
AMBER = (240, 186, 48)
AMBER_DIM = (96, 72, 20)
RED = (220, 40, 40)
RED_GLOW = (120, 20, 20)
CYAN = (90, 220, 255)
WHITE = (236, 240, 244)
DIM = (88, 98, 110)
MUTED = (52, 58, 68)
GREEN = (46, 214, 128)
BLUE = (56, 150, 255)
ORANGE = (255, 148, 48)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S2000 AP1 Phase 1 digital cluster")
    p.add_argument(
        "--windowed",
        action="store_true",
        help="Windowed 1920×1080 instead of fullscreen",
    )
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Draw a couple of frames with dummy telemetry and exit (CI / Pi check)",
    )
    p.add_argument(
        "--serial",
        metavar="PORT",
        nargs="?",
        const="/dev/ttyUSB0",
        default=None,
        help="Phase 2: read JSON from UART (default port /dev/ttyUSB0)",
    )
    return p.parse_args(argv)


class StdinSource:
    """Non-blocking JSON lines from stdin."""

    def poll(self) -> Telemetry | None:
        latest = None
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


class SerialSource:
    """Non-blocking JSON lines from optional pyserial (Phase 2)."""

    def __init__(self, port: str) -> None:
        from serial_reader import SerialUnavailable, open_serial

        try:
            self._ser = open_serial(port, baud=SERIAL_BAUD, timeout=0)
        except SerialUnavailable as e:
            print(f"serial: {e}", file=sys.stderr)
            raise SystemExit(2) from e
        self._buf = ""

    def poll(self) -> Telemetry | None:
        latest = None
        waiting = getattr(self._ser, "in_waiting", 0) or 0
        if waiting:
            chunk = self._ser.read(waiting).decode("utf-8", errors="ignore")
            self._buf += chunk
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            parsed = try_parse_line(line)
            if parsed is not None:
                latest = parsed
        return latest


def _font(pygame, size: int, bold: bool = False):
    return pygame.font.SysFont("DejaVu Sans", size, bold=bold)


def blit_text(surf, font, text: str, color, pos, anchor: str = "topleft") -> None:
    img = font.render(text, True, color)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    surf.blit(img, rect)


def draw_panel(pygame, surf, rect, radius: int = 18) -> None:
    pygame.draw.rect(surf, PANEL, rect, border_radius=radius)
    pygame.draw.rect(surf, PANEL_EDGE, rect, width=2, border_radius=radius)


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float):
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def draw_arc_sweep(
    pygame,
    surf,
    cx: int,
    cy: int,
    r_outer: int,
    r_inner: int,
    frac: float,
    start_deg: float = 210.0,
    span_deg: float = 240.0,
) -> None:
    """Filled RPM sweep: amber through the midrange, red into the limiter."""
    frac = max(0.0, min(1.0, frac))
    steps = max(2, int(120 * frac))
    for i in range(steps):
        t0 = i / 120
        t1 = (i + 1) / 120
        if t1 > frac:
            t1 = frac
        a0 = math.radians(start_deg + span_deg * t0)
        a1 = math.radians(start_deg + span_deg * t1)
        colour = AMBER if t0 < 0.82 else lerp(AMBER, RED, (t0 - 0.82) / 0.18)
        pts = [
            (cx + int(r_inner * math.cos(a0)), cy + int(r_inner * math.sin(a0))),
            (cx + int(r_outer * math.cos(a0)), cy + int(r_outer * math.sin(a0))),
            (cx + int(r_outer * math.cos(a1)), cy + int(r_outer * math.sin(a1))),
            (cx + int(r_inner * math.cos(a1)), cy + int(r_inner * math.sin(a1))),
        ]
        pygame.draw.polygon(surf, colour, pts)


def draw_rpm_gauge(pygame, fonts, surf, cx: int, cy: int, rpm: int) -> None:
    r_outer, r_inner = 310, 248
    # Track
    pygame.draw.circle(surf, (22, 26, 34), (cx, cy), r_outer + 8)
    pygame.draw.circle(surf, BG, (cx, cy), r_inner - 6)
    pygame.draw.circle(surf, MUTED, (cx, cy), r_outer, 3)
    pygame.draw.circle(surf, MUTED, (cx, cy), r_inner, 2)

    vmax = float(RPM_REDLINE)
    draw_arc_sweep(pygame, surf, cx, cy, r_outer, r_inner, rpm / vmax)

    # Ticks 0–9 ×1000
    start_deg, span_deg = 210.0, 240.0
    for i in range(10):
        t = i / 9
        a = math.radians(start_deg + span_deg * t)
        redline = i >= 8
        col = RED if redline else (AMBER if i * 1000 >= RPM_VTEC else WHITE)
        x0 = cx + int((r_outer + 4) * math.cos(a))
        y0 = cy + int((r_outer + 4) * math.sin(a))
        x1 = cx + int((r_outer + 22) * math.cos(a))
        y1 = cy + int((r_outer + 22) * math.sin(a))
        pygame.draw.line(surf, col, (x0, y0), (x1, y1), 3)
        lx = cx + int((r_outer + 48) * math.cos(a))
        ly = cy + int((r_outer + 48) * math.sin(a))
        blit_text(surf, fonts["tick"], str(i), col, (lx, ly), "center")

    # VTEC hash
    vt = RPM_VTEC / vmax
    va = math.radians(start_deg + span_deg * vt)
    pygame.draw.line(
        surf,
        CYAN,
        (cx + int(r_inner * math.cos(va)), cy + int(r_inner * math.sin(va))),
        (cx + int(r_outer * math.cos(va)), cy + int(r_outer * math.sin(va))),
        3,
    )

    rpm_col = RED if rpm >= 8800 else (AMBER if rpm >= RPM_VTEC else WHITE)
    blit_text(surf, fonts["rpm"], f"{rpm:,}", rpm_col, (cx, cy - 18), "center")
    blit_text(surf, fonts["label"], "RPM  ×1000", DIM, (cx, cy + 58), "center")
    if rpm >= RPM_VTEC:
        blit_text(surf, fonts["tiny"], "VTEC", CYAN, (cx, cy + 96), "center")


def draw_speed(pygame, fonts, surf, cx: int, cy: int, speed: float) -> None:
    blit_text(surf, fonts["speed"], f"{int(round(speed))}", WHITE, (cx, cy - 10), "center")
    blit_text(surf, fonts["label"], "km/h", DIM, (cx, cy + 110), "center")
    # Slim analog hint under the digits
    track = pygame.Rect(cx - 220, cy + 150, 440, 10)
    pygame.draw.rect(surf, MUTED, track, border_radius=5)
    frac = max(0.0, min(1.0, speed / SPEED_MAX_KMH))
    fill = pygame.Rect(track.x, track.y, int(track.w * frac), track.h)
    pygame.draw.rect(surf, AMBER if speed < 200 else RED, fill, border_radius=5)


def draw_bar(
    pygame,
    fonts,
    surf,
    x: int,
    y: int,
    w: int,
    h: int,
    frac: float,
    label: str,
    value: str,
    colour,
    warn: bool = False,
) -> None:
    blit_text(surf, fonts["tiny"], label, DIM, (x, y))
    blit_text(
        surf,
        fonts["readout"],
        value,
        RED if warn else WHITE,
        (x + w, y),
        "topright",
    )
    track = pygame.Rect(x, y + 36, w, h)
    pygame.draw.rect(surf, MUTED, track, border_radius=7)
    inner = track.inflate(-6, -6)
    fw = int(inner.w * max(0.0, min(1.0, frac)))
    if fw > 0:
        pygame.draw.rect(surf, colour, (inner.x, inner.y, fw, inner.h), border_radius=5)


def draw_lamp(
    pygame,
    fonts,
    surf,
    cx: int,
    cy: int,
    label: str,
    on: bool,
    colour,
    shape: str = "rect",
) -> None:
    col = colour if on else (28, 32, 40)
    if shape == "tri_l":
        pygame.draw.polygon(surf, col, [(cx - 22, cy), (cx + 14, cy - 16), (cx + 14, cy + 16)])
    elif shape == "tri_r":
        pygame.draw.polygon(surf, col, [(cx + 22, cy), (cx - 14, cy - 16), (cx - 14, cy + 16)])
    else:
        pygame.draw.rect(surf, col, pygame.Rect(cx - 28, cy - 16, 56, 32), border_radius=6)
    text_col = BG if on else MUTED
    blit_text(surf, fonts["lamp"], label, text_col if shape == "rect" else (col if on else MUTED), (cx, cy), "center")


def draw_cluster(pygame, fonts, surf, telem: Telemetry) -> None:
    surf.fill(BG)
    # Hood / bezel silhouette
    pygame.draw.rect(surf, (10, 12, 16), pygame.Rect(40, 30, W - 80, H - 60), border_radius=36)
    pygame.draw.rect(surf, PANEL_EDGE, pygame.Rect(40, 30, W - 80, H - 60), width=2, border_radius=36)

    blit_text(surf, fonts["tiny"], "AP1  ·  PHASE 1  ·  MOCK JSON", DIM, (W // 2, 58), "center")
    blit_text(surf, fonts["tiny"], "OVERLAY — OEM CLUSTER STAYS PLUGGED", MUTED, (W // 2, 86), "center")

    lamps = [
        ("◀", telem.lamp("turn_l"), GREEN, "tri_l"),
        ("OIL", telem.lamp("oil"), RED, "rect"),
        ("CEL", telem.lamp("cel"), ORANGE, "rect"),
        ("ABS", telem.lamp("abs"), ORANGE, "rect"),
        ("BEAM", telem.lamp("high_beam"), BLUE, "rect"),
        ("FOG", telem.lamp("fog"), GREEN, "rect"),
        ("FUEL", telem.lamp("fuel_low") or telem.fuel_pct < FUEL_LOW_PCT, ORANGE, "rect"),
        ("BATT", telem.lamp("batt_warn") or telem.batt_v < BATT_LOW_V, RED, "rect"),
        ("HOT", telem.lamp("ect_hot") or telem.ect_c >= ECT_HOT_C, RED, "rect"),
        ("▶", telem.lamp("turn_r"), GREEN, "tri_r"),
    ]
    x0 = W // 2 - (len(lamps) - 1) * 78 // 2
    for i, (label, on, col, shape) in enumerate(lamps):
        draw_lamp(pygame, fonts, surf, x0 + i * 78, 140, label, on, col, shape)

    draw_rpm_gauge(pygame, fonts, surf, 620, 560, telem.rpm)
    draw_speed(pygame, fonts, surf, 1420, 500, telem.speed_kmh)

    # Lower readouts
    fuel_warn = telem.fuel_pct < FUEL_LOW_PCT or telem.lamp("fuel_low")
    ect_warn = telem.ect_c >= ECT_HOT_C or telem.lamp("ect_hot")
    batt_warn = telem.batt_v < BATT_LOW_V or telem.lamp("batt_warn")
    fuel_col = RED if fuel_warn else GREEN
    ect_col = RED if ect_warn else (ORANGE if telem.ect_c >= 98 else GREEN)
    batt_col = RED if batt_warn else GREEN

    draw_bar(
        pygame, fonts, surf, 120, 900, 520, 28,
        telem.fuel_pct / 100.0, "FUEL", f"{telem.fuel_pct:.0f}%", fuel_col, fuel_warn,
    )
    draw_bar(
        pygame, fonts, surf, 700, 900, 520, 28,
        max(0.0, min(1.0, (telem.ect_c - 40.0) / 80.0)),
        "ECT", f"{telem.ect_c:.0f}°C", ect_col, ect_warn,
    )
    blit_text(surf, fonts["tiny"], "BATT", DIM, (1320, 900))
    blit_text(
        surf,
        fonts["readout"],
        f"{telem.batt_v:.1f} V",
        RED if batt_warn else WHITE,
        (1320, 936),
    )
    blit_text(surf, fonts["tiny"], "ODO  (display only)", DIM, (1580, 900))
    blit_text(surf, fonts["readout"], f"{telem.odo_km:,.1f} km", WHITE, (1580, 936))


def sample_telem() -> Telemetry:
    return Telemetry(
        rpm=6420,
        speed_kmh=98.0,
        fuel_pct=41.0,
        ect_c=89.0,
        batt_v=14.05,
        odo_km=142_857.3,
        lamps={
            "oil": False,
            "cel": False,
            "abs": False,
            "turn_l": True,
            "turn_r": False,
            "high_beam": True,
            "fog": False,
            "fuel_low": False,
            "batt_warn": False,
            "ect_hot": False,
        },
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.smoke:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    try:
        import pygame
    except ImportError:
        print("pygame is required: pip install -r requirements.txt", file=sys.stderr)
        raise SystemExit(1)

    pygame.init()
    pygame.display.set_caption("S2000 AP1 — Phase 1")
    flags = 0 if (args.windowed or args.smoke) else pygame.FULLSCREEN
    try:
        screen = pygame.display.set_mode((W, H), flags)
    except pygame.error:
        screen = pygame.display.set_mode((W, H))

    fonts = {
        "speed": _font(pygame, 200, bold=True),
        "rpm": _font(pygame, 92, bold=True),
        "tick": _font(pygame, 22, bold=True),
        "label": _font(pygame, 28),
        "readout": _font(pygame, 36, bold=True),
        "tiny": _font(pygame, 20),
        "lamp": _font(pygame, 16, bold=True),
    }
    clock = pygame.time.Clock()

    if args.serial:
        source: StdinSource | SerialSource = SerialSource(args.serial)
    else:
        source = StdinSource()

    telem = sample_telem() if args.smoke else Telemetry()
    running = True
    frames = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

        incoming = source.poll()
        if incoming is not None:
            telem = incoming

        draw_cluster(pygame, fonts, screen, telem)
        pygame.display.flip()
        clock.tick(60)
        frames += 1
        if args.smoke and frames >= 3:
            running = False

    pygame.quit()


if __name__ == "__main__":
    main()
