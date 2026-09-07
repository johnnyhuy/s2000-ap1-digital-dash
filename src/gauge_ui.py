#!/usr/bin/env python3
"""Phase 1 OEM-geometry AP1 cluster — amber LCD in a hooded cowl.

Reads Telemetry JSON lines from stdin (or --serial in Phase 2).

  python mock_telemetry.py | python gauge_ui.py
  python gauge_ui.py --windowed --intro
  python gauge_ui.py --smoke --screenshot shots

Esc or Q quits. Space skips the boot intro.
"""
from __future__ import annotations

import argparse
import math
import os
import select
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocol import (
    BATT_LOW_V,
    ECT_HOT_C,
    FUEL_LOW_PCT,
    RPM_REDLINE,
    SERIAL_BAUD,
    Telemetry,
    try_parse_line,
)

W, H = 1920, 1080

# Cabin around the module — not a full-bleed app chrome
CABIN = (7, 7, 8)
CABIN_LIFT = (14, 13, 12)
COWL = (16, 15, 14)
COWL_HIGH = (38, 34, 30)
COWL_EDGE = (52, 46, 40)
WELL = (4, 4, 5)
LCD = (2, 2, 3)
AMBER = (236, 168, 36)
AMBER_DIM = (72, 48, 12)
AMBER_GHOST = (28, 20, 8)
RED = (210, 36, 32)
RED_DIM = (78, 16, 14)
CYAN = (72, 210, 230)
WHITE = (230, 226, 214)
DIM = (92, 84, 70)
MUTED = (42, 38, 34)
GREEN = (52, 200, 110)
ORANGE = (230, 132, 36)

# Shallow rainbow in pygame coords (y-down): 0°=+x, 90°=+y/down, 270°=up
TACH_START_DEG = 204.0
TACH_SPAN_DEG = 132.0
TACH_CX, TACH_CY = 960, 868
TACH_R_NUM = 548
TACH_R_OUTER = 498
TACH_R_INNER = 428
TACH_SEGS = 90
TEMP_SEGS = 6
FUEL_SEGS = 21

# ID.4-inspired boot: sweep → READY summary → gauge reveal → live
PHASE_SWEEP_S = 1.35
PHASE_READY_S = 1.75
PHASE_REVEAL_S = 1.55


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S2000 AP1 OEM-geometry digital cluster")
    p.add_argument("--windowed", action="store_true", help="1920×1080 window instead of fullscreen")
    p.add_argument(
        "--smoke",
        action="store_true",
        help="Dummy SDL, draw a few frames, optional screenshots, then exit",
    )
    intro = p.add_mutually_exclusive_group()
    intro.add_argument(
        "--intro",
        dest="intro",
        action="store_true",
        help="Play the ID.4-style boot (default when not --smoke)",
    )
    intro.add_argument(
        "--no-intro",
        dest="intro",
        action="store_false",
        help="Skip boot and go straight to live gauges",
    )
    p.set_defaults(intro=None)
    p.add_argument(
        "--screenshot",
        metavar="DIR",
        default=None,
        help="Write PNG frames (sweep/ready/reveal/live) into DIR",
    )
    p.add_argument(
        "--serial",
        metavar="PORT",
        nargs="?",
        const="/dev/ttyUSB0",
        default=None,
        help="Phase 2: read JSON from UART (default port /dev/ttyUSB0)",
    )
    args = p.parse_args(argv)
    if args.intro is None:
        args.intro = not args.smoke
    return args


def clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_colour(
    a: tuple[int, int, int], b: tuple[int, int, int], t: float
) -> tuple[int, int, int]:
    t = clamp(t, 0.0, 1.0)
    return (
        int(a[0] + (b[0] - a[0]) * t),
        int(a[1] + (b[1] - a[1]) * t),
        int(a[2] + (b[2] - a[2]) * t),
    )


def exp_smooth(current: float, target: float, dt: float, tau: float) -> float:
    """Frame-rate independent approach toward target (tau ≈ seconds to settle)."""
    if tau <= 0 or dt <= 0:
        return target
    k = 1.0 - math.exp(-dt / tau)
    return current + (target - current) * k


def tach_angle(frac: float) -> float:
    """Radians along the OEM tach arc (0 at 0×1000, 1 at 9×1000)."""
    return math.radians(TACH_START_DEG + TACH_SPAN_DEG * clamp(frac, 0.0, 1.0))


def tach_point(r: float, frac: float) -> tuple[int, int]:
    a = tach_angle(frac)
    return (
        TACH_CX + int(r * math.cos(a)),
        TACH_CY + int(r * math.sin(a)),
    )


def ect_frac(ect_c: float) -> float:
    """0 at cold (C), 1 at hot (H). OEM-ish 40–105 °C window."""
    return clamp((ect_c - 40.0) / 65.0, 0.0, 1.0)


def fuel_frac(fuel_pct: float) -> float:
    return clamp(fuel_pct / 100.0, 0.0, 1.0)


def intro_phase_at(t: float) -> tuple[str, float]:
    """Return (phase_name, local 0–1) for the boot clock."""
    if t < 0:
        t = 0.0
    if t < PHASE_SWEEP_S:
        return "sweep", t / PHASE_SWEEP_S
    t -= PHASE_SWEEP_S
    if t < PHASE_READY_S:
        return "ready", t / PHASE_READY_S
    t -= PHASE_READY_S
    if t < PHASE_REVEAL_S:
        return "reveal", t / PHASE_REVEAL_S
    return "live", 1.0


def intro_duration_s() -> float:
    return PHASE_SWEEP_S + PHASE_READY_S + PHASE_REVEAL_S


def reveal_rpm(local_t: float, live_rpm: float) -> float:
    """Self-test: 0 → redline, then settle onto live RPM."""
    t = clamp(local_t, 0.0, 1.0)
    if t < 0.58:
        return RPM_REDLINE * (t / 0.58)
    return lerp(float(RPM_REDLINE), live_rpm, (t - 0.58) / 0.42)


@dataclass
class DisplayState:
    """Smoothed face values. Lamps snap; needles lerp."""

    rpm: float = 0.0
    speed_kmh: float = 0.0
    fuel_pct: float = 50.0
    ect_c: float = 20.0
    batt_v: float = 12.4
    odo_km: float = 0.0
    trip_km: float = 0.0
    lamps: dict[str, bool] = field(default_factory=dict)
    trip_origin: float | None = None

    def snap(self, telem: Telemetry) -> None:
        self.rpm = float(telem.rpm)
        self.speed_kmh = float(telem.speed_kmh)
        self.fuel_pct = float(telem.fuel_pct)
        self.ect_c = float(telem.ect_c)
        self.batt_v = float(telem.batt_v)
        self.odo_km = float(telem.odo_km)
        self.lamps = dict(telem.lamps)
        if self.trip_origin is None:
            self.trip_origin = self.odo_km
        self.trip_km = max(0.0, self.odo_km - self.trip_origin)

    def follow(self, telem: Telemetry, dt: float) -> None:
        self.rpm = exp_smooth(self.rpm, float(telem.rpm), dt, 0.07)
        self.speed_kmh = exp_smooth(self.speed_kmh, float(telem.speed_kmh), dt, 0.11)
        self.fuel_pct = exp_smooth(self.fuel_pct, float(telem.fuel_pct), dt, 0.35)
        self.ect_c = exp_smooth(self.ect_c, float(telem.ect_c), dt, 0.40)
        self.batt_v = exp_smooth(self.batt_v, float(telem.batt_v), dt, 0.22)
        self.odo_km = float(telem.odo_km)
        self.lamps = dict(telem.lamps)
        if self.trip_origin is None:
            self.trip_origin = self.odo_km
        self.trip_km = max(0.0, self.odo_km - self.trip_origin)


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


def _font(pygame, size: int, bold: bool = False, mono: bool = False):
    names = (
        ("DejaVu Sans Mono", "FreeMono", "monospace")
        if mono
        else ("DejaVu Sans", "FreeSans", "sans-serif")
    )
    return pygame.font.SysFont(list(names), size, bold=bold)


def blit_text(surf, font, text: str, color, pos, anchor: str = "topleft") -> None:
    img = font.render(text, True, color)
    rect = img.get_rect()
    setattr(rect, anchor, pos)
    surf.blit(img, rect)


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


def _cowl_rects() -> tuple:
    """Module + LCD well. Cluster sits as a hooded unit, not full-bleed UI."""
    module = (130, 118, 1660, 844)
    well = (210, 214, 1500, 668)
    return module, well


def draw_cabin(pygame, surf) -> None:
    surf.fill(CABIN)
    # Soft dash lift behind the module so the cowl reads as a physical cluster
    pygame.draw.ellipse(surf, CABIN_LIFT, pygame.Rect(40, 40, W - 80, H - 80))
    pygame.draw.ellipse(surf, CABIN, pygame.Rect(120, 90, W - 240, H - 180))


def draw_cowl(pygame, surf, sweep_t: float | None = None) -> None:
    module, well = _cowl_rects()
    mx, my, mw, mh = module
    wx, wy, ww, wh = well

    shadow = pygame.Rect(mx + 18, my + 28, mw, mh)
    pygame.draw.rect(surf, (2, 2, 3), shadow, border_radius=70)

    body = pygame.Rect(mx, my, mw, mh)
    pygame.draw.rect(surf, COWL, body, border_radius=64)
    pygame.draw.rect(surf, COWL_EDGE, body, width=3, border_radius=64)

    # Hood / arched visor — physical cowl, not a screen-chrome title bar
    hood = pygame.Rect(mx + 20, my - 36, mw - 40, 248)
    pygame.draw.ellipse(surf, (11, 10, 10), hood)
    pygame.draw.arc(surf, COWL_HIGH, hood.inflate(12, 16), math.radians(18), math.radians(162), 7)
    pygame.draw.arc(surf, (8, 7, 7), pygame.Rect(wx - 10, wy - 70, ww + 20, 180), math.radians(12), math.radians(168), 18)

    well_rect = pygame.Rect(wx, wy, ww, wh)
    pygame.draw.rect(surf, WELL, well_rect, border_radius=38)
    pygame.draw.rect(surf, (22, 18, 14), well_rect, width=2, border_radius=38)

    glass = well_rect.inflate(-16, -16)
    pygame.draw.rect(surf, LCD, glass, border_radius=30)

    if sweep_t is not None:
        # ID. Light-style welcome: a band travels the hood lip
        band_w = 280
        x = mx + 80 + int((mw - 160 - band_w) * clamp(sweep_t, 0.0, 1.0))
        col = lerp_colour(AMBER, CYAN, sweep_t)
        pygame.draw.rect(surf, col, pygame.Rect(x, my + 28, band_w, 10), border_radius=5)


def draw_tach_segments(
    pygame,
    surf,
    lit_frac: float,
    ghost: bool = True,
) -> None:
    """Dense linear LCD bars along the arch. 8–9 are thick red blocks."""
    for i in range(TACH_SEGS):
        t0 = i / TACH_SEGS
        t1 = (i + 1) / TACH_SEGS
        mid = (t0 + t1) * 0.5
        redline = mid >= (8.0 / 9.0)
        on = mid <= lit_frac + 1e-6
        if redline:
            r_out, r_in = TACH_R_OUTER + 10, TACH_R_INNER - 8
            col = RED if on else (36, 12, 10)
        else:
            r_out, r_in = TACH_R_OUTER, TACH_R_INNER
            col = AMBER if on else (AMBER_GHOST if ghost else LCD)
        pad = 0.12
        a0 = tach_angle(t0 + (t1 - t0) * pad)
        a1 = tach_angle(t1 - (t1 - t0) * pad)
        pts = [
            (TACH_CX + int(r_in * math.cos(a0)), TACH_CY + int(r_in * math.sin(a0))),
            (TACH_CX + int(r_out * math.cos(a0)), TACH_CY + int(r_out * math.sin(a0))),
            (TACH_CX + int(r_out * math.cos(a1)), TACH_CY + int(r_out * math.sin(a1))),
            (TACH_CX + int(r_in * math.cos(a1)), TACH_CY + int(r_in * math.sin(a1))),
        ]
        pygame.draw.polygon(surf, col, pts)


def draw_tach_numbers(fonts, surf, dim: bool = False) -> None:
    for i in range(10):
        hot = i >= 8
        col = (RED if hot else AMBER) if not dim else (RED_DIM if hot else AMBER_DIM)
        pos = tach_point(TACH_R_NUM, i / 9)
        blit_text(surf, fonts["tick"], str(i), col, pos, "center")
    blit_text(surf, fonts["micro"], "×1000", DIM if not dim else MUTED, (268, 268), "center")


def draw_temp_stack(pygame, fonts, surf, frac: float, hot: bool) -> None:
    """Vertical TEMP C–H on the LEFT of the speed (AP1 straight stack)."""
    x, y, w, h = 318, 430, 46, 248
    blit_text(surf, fonts["tiny"], "C", AMBER, (x + w // 2, y - 18), "center")
    blit_text(surf, fonts["micro"], "TEMP", DIM, (x + w // 2, y - 42), "center")
    gap = 5
    seg_h = (h - gap * (TEMP_SEGS - 1)) / TEMP_SEGS
    lit = int(round(frac * TEMP_SEGS))
    for i in range(TEMP_SEGS):
        # i=0 is C (top); fill toward H as ECT rises
        sy = y + i * (seg_h + gap)
        on = i < lit
        col = RED if (on and (hot or i >= TEMP_SEGS - 1 and frac > 0.92)) else (AMBER if on else AMBER_GHOST)
        pygame.draw.rect(surf, col, pygame.Rect(x, int(sy), w, int(seg_h)), border_radius=3)
    blit_text(surf, fonts["tiny"], "H", RED if hot else AMBER, (x + w // 2, y + h + 16), "center")


def draw_fuel_bar(pygame, fonts, surf, frac: float, low: bool) -> None:
    """Horizontal FUEL E–F on the RIGHT of the speed (AP1 straight bar)."""
    x, y, w, h = 1324, 572, 268, 36
    blit_text(surf, fonts["micro"], "FUEL", DIM, (x + w // 2, y - 36), "center")
    blit_text(surf, fonts["tiny"], "E", RED if low else AMBER, (x - 18, y + h // 2), "center")
    blit_text(surf, fonts["tiny"], "F", AMBER, (x + w + 18, y + h // 2), "center")
    gap = 3
    seg_w = (w - gap * (FUEL_SEGS - 1)) / FUEL_SEGS
    lit = int(round(frac * FUEL_SEGS))
    low_mark = max(1, int(round((FUEL_LOW_PCT / 100.0) * FUEL_SEGS)))
    for i in range(FUEL_SEGS):
        sx = x + i * (seg_w + gap)
        on = i < lit
        warn = i < low_mark
        if on:
            col = RED if (low or warn and i == 0) else AMBER
        else:
            col = RED_DIM if warn and i == 0 else AMBER_GHOST
        pygame.draw.rect(surf, col, pygame.Rect(int(sx), y, max(3, int(seg_w)), h), border_radius=2)


def draw_speed(fonts, surf, speed: float) -> None:
    digits = f"{int(round(clamp(speed, 0.0, 399.0))):d}"
    blit_text(surf, fonts["speed"], digits, AMBER, (960, 538), "center")
    blit_text(surf, fonts["label"], "km/h", DIM, (960, 638), "center")


def draw_odo_row(fonts, surf, face: DisplayState, batt_warn: bool) -> None:
    y = 718
    blit_text(surf, fonts["micro"], "ODO km", DIM, (620, y), "center")
    blit_text(surf, fonts["readout"], f"{face.odo_km:,.1f}", AMBER, (620, y + 26), "center")
    blit_text(surf, fonts["micro"], "TRIP A km", DIM, (960, y), "center")
    blit_text(surf, fonts["readout"], f"{face.trip_km:,.1f}", AMBER, (960, y + 26), "center")
    blit_text(surf, fonts["micro"], "BATT", DIM, (1300, y), "center")
    blit_text(
        surf,
        fonts["readout"],
        f"{face.batt_v:.1f} V",
        RED if batt_warn else AMBER,
        (1300, y + 26),
        "center",
    )


def _lamp_states(face: DisplayState, bulb_check: bool = False) -> list[tuple[str, bool, tuple[int, int, int], str]]:
    if bulb_check:
        return [
            ("◀", True, GREEN, "tri_l"),
            ("OIL", True, RED, "rect"),
            ("CEL", True, ORANGE, "rect"),
            ("ABS", True, ORANGE, "rect"),
            ("HI", True, CYAN, "rect"),
            ("FOG", True, GREEN, "rect"),
            ("FUEL", True, ORANGE, "rect"),
            ("BAT", True, RED, "rect"),
            ("HOT", True, RED, "rect"),
            ("▶", True, GREEN, "tri_r"),
        ]
    return [
        ("◀", face.lamps.get("turn_l", False), GREEN, "tri_l"),
        ("OIL", face.lamps.get("oil", False), RED, "rect"),
        ("CEL", face.lamps.get("cel", False), ORANGE, "rect"),
        ("ABS", face.lamps.get("abs", False), ORANGE, "rect"),
        ("HI", face.lamps.get("high_beam", False), CYAN, "rect"),
        ("FOG", face.lamps.get("fog", False), GREEN, "rect"),
        (
            "FUEL",
            face.lamps.get("fuel_low", False) or face.fuel_pct < FUEL_LOW_PCT,
            ORANGE,
            "rect",
        ),
        (
            "BAT",
            face.lamps.get("batt_warn", False) or face.batt_v < BATT_LOW_V,
            RED,
            "rect",
        ),
        (
            "HOT",
            face.lamps.get("ect_hot", False) or face.ect_c >= ECT_HOT_C,
            RED,
            "rect",
        ),
        ("▶", face.lamps.get("turn_r", False), GREEN, "tri_r"),
    ]


def draw_lamp_strip(pygame, fonts, surf, face: DisplayState, bulb_check: bool = False) -> None:
    lamps = _lamp_states(face, bulb_check=bulb_check)
    y = 812
    x0 = W // 2 - (len(lamps) - 1) * 86 // 2
    for i, (label, on, colour, shape) in enumerate(lamps):
        cx = x0 + i * 86
        col = colour if on else AMBER_GHOST
        if shape == "tri_l":
            pygame.draw.polygon(surf, col, [(cx - 20, y), (cx + 14, y - 14), (cx + 14, y + 14)])
        elif shape == "tri_r":
            pygame.draw.polygon(surf, col, [(cx + 20, y), (cx - 14, y - 14), (cx - 14, y + 14)])
        else:
            pygame.draw.rect(surf, col if on else (16, 14, 12), pygame.Rect(cx - 30, y - 14, 60, 28), border_radius=5)
            blit_text(surf, fonts["lamp"], label, WHITE if on else MUTED, (cx, y), "center")


def draw_ready_card(fonts, surf, face: DisplayState) -> None:
    """ID.4-like pre-drive summary sitting in the LCD well."""
    blit_text(surf, fonts["micro"], "HONDA  S2000  AP1", DIM, (960, 360), "center")
    blit_text(surf, fonts["ready"], "READY", AMBER, (960, 470), "center")
    blit_text(surf, fonts["tiny"], "IGNITION ON  ·  SYSTEMS OK", DIM, (960, 548), "center")
    chips = [
        ("BATT", f"{face.batt_v:.1f} V"),
        ("FUEL", f"{face.fuel_pct:.0f} %"),
        ("TEMP", f"{face.ect_c:.0f} °C"),
        ("ODO", f"{face.odo_km:,.0f} km"),
    ]
    x0 = 430
    for i, (name, val) in enumerate(chips):
        x = x0 + i * 270
        blit_text(surf, fonts["micro"], name, DIM, (x, 640), "center")
        blit_text(surf, fonts["readout"], val, AMBER, (x, 672), "center")


def draw_live_face(
    pygame,
    fonts,
    surf,
    face: DisplayState,
    rpm_override: float | None = None,
    bulb_check: bool = False,
    fade: float = 1.0,
) -> None:
    rpm = face.rpm if rpm_override is None else rpm_override
    layer = surf
    if fade < 0.999:
        layer = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    draw_tach_segments(pygame, layer, clamp(rpm / float(RPM_REDLINE), 0.0, 1.0))
    draw_tach_numbers(fonts, layer)
    draw_temp_stack(pygame, fonts, layer, ect_frac(face.ect_c), face.ect_c >= ECT_HOT_C)
    draw_fuel_bar(pygame, fonts, layer, fuel_frac(face.fuel_pct), face.fuel_pct < FUEL_LOW_PCT)
    draw_speed(fonts, layer, face.speed_kmh)
    draw_odo_row(
        fonts,
        layer,
        face,
        face.batt_v < BATT_LOW_V or face.lamps.get("batt_warn", False),
    )
    draw_lamp_strip(pygame, fonts, layer, face, bulb_check=bulb_check)
    if fade < 0.999:
        layer.set_alpha(int(255 * clamp(fade, 0.0, 1.0)))
        surf.blit(layer, (0, 0))


def draw_caption(fonts, surf) -> None:
    blit_text(
        surf,
        fonts["micro"],
        "OVERLAY MODULE  ·  OEM CLUSTER STAYS PLUGGED  ·  DISPLAY-ONLY ODO",
        MUTED,
        (W // 2, 1008),
        "center",
    )


def draw_frame(
    pygame,
    fonts,
    surf,
    face: DisplayState,
    phase: str,
    phase_t: float,
) -> None:
    draw_cabin(pygame, surf)
    draw_cowl(pygame, surf, sweep_t=phase_t if phase == "sweep" else None)
    if phase == "sweep":
        # Dim ghost of the LCD so the sweep reads as a wake-up, not an empty hole
        draw_tach_segments(pygame, surf, 0.0, ghost=True)
        draw_tach_numbers(fonts, surf, dim=True)
    elif phase == "ready":
        draw_ready_card(fonts, surf, face)
    elif phase == "reveal":
        draw_live_face(
            pygame,
            fonts,
            surf,
            face,
            rpm_override=reveal_rpm(phase_t, face.rpm),
            bulb_check=phase_t < 0.55,
            fade=clamp(phase_t * 1.4, 0.0, 1.0),
        )
    else:
        draw_live_face(pygame, fonts, surf, face)
    draw_caption(fonts, surf)


SCREENSHOT_SCENES: tuple[tuple[str, str, float], ...] = (
    ("01_sweep", "sweep", 0.55),
    ("02_ready", "ready", 0.55),
    ("03_reveal", "reveal", 0.62),
    ("04_live", "live", 1.0),
)


def write_screenshots(pygame, fonts, face: DisplayState, dest: Path) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    canvas = pygame.Surface((W, H))
    for name, phase, local_t in SCREENSHOT_SCENES:
        draw_frame(pygame, fonts, canvas, face, phase, local_t)
        path = dest / f"{name}.png"
        pygame.image.save(canvas, str(path))
        written.append(path)
    return written


def build_fonts(pygame) -> dict:
    return {
        "speed": _font(pygame, 168, bold=True, mono=True),
        "ready": _font(pygame, 92, bold=True),
        "tick": _font(pygame, 28, bold=True),
        "label": _font(pygame, 26),
        "readout": _font(pygame, 30, bold=True, mono=True),
        "tiny": _font(pygame, 22, bold=True),
        "micro": _font(pygame, 16),
        "lamp": _font(pygame, 15, bold=True),
    }


def init_pygame(windowed: bool, headless: bool):
    import pygame

    pygame.init()
    pygame.display.set_caption("S2000 AP1 — OEM cluster")
    flags = 0 if (windowed or headless) else pygame.FULLSCREEN
    try:
        screen = pygame.display.set_mode((W, H), flags)
    except pygame.error:
        screen = pygame.display.set_mode((W, H))
    return pygame, screen


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if args.smoke:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    try:
        import pygame as _pygame_probe  # noqa: F401
    except ImportError:
        print("pygame is required: pip install -r requirements.txt", file=sys.stderr)
        raise SystemExit(1)

    pygame, screen = init_pygame(args.windowed, headless=args.smoke)
    fonts = build_fonts(pygame)
    clock = pygame.time.Clock()

    if args.serial:
        source: StdinSource | SerialSource = SerialSource(args.serial)
    else:
        source = StdinSource()

    telem = sample_telem() if args.smoke else Telemetry()
    face = DisplayState()
    if args.smoke:
        face.snap(telem)
        face.trip_origin = telem.odo_km - 128.4
        face.trip_km = 128.4
    else:
        face.snap(telem)

    if args.screenshot:
        paths = write_screenshots(pygame, fonts, face, Path(args.screenshot))
        for path in paths:
            print(path)

    if args.smoke:
        # Exercise a couple of live frames after optional screenshot dump
        for _ in range(3):
            draw_frame(pygame, fonts, screen, face, "live", 1.0)
            pygame.display.flip()
        pygame.quit()
        return

    boot_t = 0.0
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    args.intro = False

        incoming = source.poll()
        if incoming is not None:
            telem = incoming

        face.follow(telem, dt)

        if args.intro:
            boot_t += dt
            phase, phase_t = intro_phase_at(boot_t)
            if phase == "live":
                args.intro = False
        else:
            phase, phase_t = "live", 1.0

        draw_frame(pygame, fonts, screen, face, phase, phase_t)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
