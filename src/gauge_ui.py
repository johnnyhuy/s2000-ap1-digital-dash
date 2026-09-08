#!/usr/bin/env python3
"""Phase 1 OEM-geometry AP1 cluster — amber LCD in a hooded cowl.

Reads Telemetry JSON lines from stdin (or --serial in Phase 2).

  python mock_telemetry.py | python gauge_ui.py
  python -m mocks.esp32_uart --count 40 --immediate | python gauge_ui.py --smoke
  python gauge_ui.py --windowed --intro
  python gauge_ui.py --smoke --screenshot shots

Esc or Q quits. Space skips the boot intro.

Face proportions are locked in `refs/flat/DIMENSIONS.md` (percent of the
module bounding box). Protocol JSON field names are unchanged.
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
from lcd_digits import blit_digits, lcd_window
from oem_icons import (
    LAMP_GHOST,
    blit_glow,
    icon_surface,
    lamp_states,
    lamp_strip_inner_width,
)
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

# Cabin around the module — flat orthographic, no fake 3D skew
CABIN = (8, 8, 9)
COWL = (18, 17, 16)
COWL_HIGH = (44, 40, 36)
COWL_EDGE = (58, 52, 46)
WELL = (8, 6, 4)
LCD = (6, 4, 2)
AMBER = (236, 152, 32)
AMBER_HOT = (255, 176, 46)
AMBER_DIM = (78, 50, 14)
AMBER_GHOST = (40, 26, 10)
AMBER_WASH = (52, 38, 12)
RED = (214, 36, 30)
RED_DIM = (78, 16, 14)
RED_GHOST = (42, 14, 12)
WHITE = (230, 226, 214)
DIM = (92, 84, 70)
MUTED = (42, 38, 34)
ORANGE = (230, 132, 36)
BEZEL_BTN = (118, 118, 116)
BEZEL_BAND = (14, 15, 16)
BEZEL_BAND_EDGE = (32, 34, 36)

# --- locked % layout (see refs/flat/DIMENSIONS.md) ---------------------------
# Module as % of the 1920×1080 canvas; height from OEM 2.35:1 elevation
MODULE_X_PCT = 0.040
MODULE_W_PCT = 0.920
MODULE_ASPECT = 2.35
# Within the module (0,0 = module top-left) — locked from the flat OEM drawing
STEP_W_PCT = 0.044          # rectangular side-notch depth
NOTCH_TOP_PCT = 0.58        # notch y-range (OEM lock)
NOTCH_BOT_PCT = 0.72
ARCH_RISE_PCT = 0.28        # y% = 28 * u² from the module top
LAMP_Y_PCT = 0.805          # hardware strip centre-line
BEZEL_H_PCT = 0.175
LCD_INSET_X_PCT = 0.010
LCD_TOP_PCT = 0.055
LCD_BOTTOM_PCT = 0.76       # just under TEMP / FUEL
ARCH_N = 2.0                # parabola (u²)
TEMP_X_PCT, TEMP_Y_PCT, TEMP_W_PCT = 0.075, 0.72, 0.180
FUEL_X_PCT, FUEL_Y_PCT, FUEL_W_PCT = 0.745, 0.72, 0.180
BAR_H_PCT = 0.030
SPEED_X_PCT, SPEED_Y_PCT = 0.50, 0.40
ODO_Y_PCT = 0.50            # directly under the speed (OEM lock)
TACH_END_Y_PCT = 0.64
TACH_PEAK_Y_PCT = 0.12
TACH_INSET_X_PCT = 0.090

# OEM AP1: 6 coolant bars, a finer fuel ladder (photos ~10–16 visible)
TEMP_SEGS = 6
FUEL_SEGS = 16
REDLINE_BLOCKS = 5
TACH_MAJORS = 10  # 0..9
TACH_MINORS_PER = 4  # 200 r/min ticks between majors (OEM)

# ID.4-inspired boot: sweep → READY summary → gauge reveal → live
PHASE_SWEEP_S = 1.35
PHASE_READY_S = 1.75
PHASE_REVEAL_S = 1.55


@dataclass(frozen=True)
class FaceGeom:
    """Pixel geometry derived from the locked OEM percentages."""

    module: tuple[int, int, int, int]
    lcd: tuple[int, int, int, int]
    bezel: tuple[int, int, int, int]
    step: int
    spring_y: int
    hood_peak_y: int
    lcd_peak_y: int
    lcd_spring_y: int
    notch_top_y: int
    notch_bot_y: int
    temp: tuple[int, int, int, int]
    fuel: tuple[int, int, int, int]
    speed_c: tuple[int, int]
    odo_c: tuple[int, int]
    tach_cx: int
    tach_cy: int
    tach_r_outer: int
    tach_r_inner: int
    tach_r_num: int
    tach_start_deg: float
    tach_span_deg: float
    arch_n: float
    rocker: tuple[int, int, int, int]
    lamp_band: tuple[int, int, int, int]
    trip: tuple[int, int, int, int]
    trip_blank: tuple[int, int, int, int]


def _pct(v: float) -> int:
    return int(round(v))


def build_face_geom(w: int = W, h: int = H) -> FaceGeom:
    """Build the flat AP1 face. Percentages match refs/flat/DIMENSIONS.md."""
    mx = _pct(w * MODULE_X_PCT)
    mw = _pct(w * MODULE_W_PCT)
    mh = _pct(mw / MODULE_ASPECT)
    my = _pct((h - mh) * 0.42)  # sit slightly high so the caption clears
    step = _pct(mw * STEP_W_PCT)
    bezel_h = _pct(mh * BEZEL_H_PCT)
    bezel_y = my + _pct(mh * LAMP_Y_PCT)
    notch_top_y = my + _pct(mh * NOTCH_TOP_PCT)
    notch_bot_y = my + _pct(mh * NOTCH_BOT_PCT)
    inset = _pct(mw * LCD_INSET_X_PCT)
    lcd_x = mx + step + inset
    lcd_w = mw - 2 * step - 2 * inset
    lcd_bottom = my + _pct(mh * LCD_BOTTOM_PCT)
    lcd_peak = my + _pct(mh * LCD_TOP_PCT)
    spring = my + _pct(mh * ARCH_RISE_PCT)
    lcd_y = lcd_peak
    lcd_h = lcd_bottom - lcd_peak
    lcd_spring = spring - _pct(mh * 0.02)

    bar_h = max(10, _pct(mh * BAR_H_PCT))
    temp = (
        mx + _pct(mw * TEMP_X_PCT),
        my + _pct(mh * TEMP_Y_PCT),
        _pct(mw * TEMP_W_PCT),
        bar_h,
    )
    fuel = (
        mx + _pct(mw * FUEL_X_PCT),
        my + _pct(mh * FUEL_Y_PCT),
        _pct(mw * FUEL_W_PCT),
        bar_h,
    )

    cx = mx + _pct(mw * SPEED_X_PCT)
    # Circular tach through lower-left, peak, lower-right of the LCD
    end_y = my + _pct(mh * TACH_END_Y_PCT)
    peak_y = my + _pct(mh * TACH_PEAK_Y_PCT)
    end_inset = _pct(lcd_w * TACH_INSET_X_PCT)
    x0 = lcd_x + end_inset
    x1 = lcd_x + lcd_w - end_inset
    half = (x1 - x0) / 2.0
    drop = float(end_y - peak_y)
    # R from (half, drop) chord: R = (half² + drop²) / (2 drop)
    tach_r = (half * half + drop * drop) / (2.0 * drop) if drop > 1 else half
    tach_cy = peak_y + tach_r
    start_deg = math.degrees(math.atan2(end_y - tach_cy, x0 - cx))
    end_deg = math.degrees(math.atan2(end_y - tach_cy, x1 - cx))
    if end_deg < start_deg:
        end_deg += 360.0
    span = end_deg - start_deg
    tach_r_outer = int(round(tach_r))
    tach_r_inner = tach_r_outer - 52
    tach_r_num = tach_r_inner - 12

    # Hardware strip: rocker left, dense lamp band centre, TRIP pair right
    pad = _pct(mw * 0.018)
    btn_h = _pct(bezel_h * 0.48)
    btn_y = bezel_y + (bezel_h - btn_h) // 2
    rocker_w = _pct(mw * 0.092)
    rocker = (mx + pad, btn_y, rocker_w, btn_h)
    trip_w = _pct(mw * 0.062)
    trip = (mx + mw - pad - trip_w, btn_y, trip_w, btn_h)
    trip_blank = (trip[0] - trip_w - 10, btn_y, trip_w, btn_h)
    band_h = _pct(bezel_h * 0.58)
    band_y = bezel_y + (bezel_h - band_h) // 2
    # Hug the OEM telltale strip (variable pitch: BRAKE / MAINT are wider)
    pack_w = lamp_strip_inner_width() + 28
    gap_l = rocker[0] + rocker_w + _pct(mw * 0.118)
    gap_r = trip_blank[0] - 16
    mid = (gap_l + gap_r) // 2
    lamp_band = (mid - pack_w // 2, band_y, pack_w, band_h)

    return FaceGeom(
        module=(mx, my, mw, mh),
        lcd=(lcd_x, lcd_y, lcd_w, lcd_h),
        bezel=(mx, bezel_y, mw, bezel_h),
        step=step,
        spring_y=spring,
        hood_peak_y=my,
        lcd_peak_y=lcd_peak,
        lcd_spring_y=lcd_spring,
        notch_top_y=notch_top_y,
        notch_bot_y=notch_bot_y,
        temp=temp,
        fuel=fuel,
        speed_c=(cx, my + _pct(mh * SPEED_Y_PCT)),
        odo_c=(cx, my + _pct(mh * ODO_Y_PCT)),
        tach_cx=cx,
        tach_cy=int(round(tach_cy)),
        tach_r_outer=tach_r_outer,
        tach_r_inner=tach_r_inner,
        tach_r_num=tach_r_num,
        tach_start_deg=start_deg,
        tach_span_deg=span,
        arch_n=ARCH_N,
        rocker=rocker,
        lamp_band=lamp_band,
        trip=trip,
        trip_blank=trip_blank,
    )


FACE = build_face_geom()
TACH_CX, TACH_CY = FACE.tach_cx, FACE.tach_cy
TACH_R_NUM = FACE.tach_r_num
TACH_R_OUTER = FACE.tach_r_outer
TACH_R_INNER = FACE.tach_r_inner
TACH_START_DEG = FACE.tach_start_deg
TACH_SPAN_DEG = FACE.tach_span_deg


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
        help="Write PNG frames (sweep/ready/reveal/live/cruise) into DIR",
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


def tach_arch_xy(frac: float, g: FaceGeom = FACE) -> tuple[float, float]:
    """Place a tach tick on the OEM parabola (not a circular wedge).

    frac 0 → 0×1000 at the lower left; frac 1 → 9×1000 at the lower right.
    """
    lx, _, lw, _ = g.lcd
    inset = lw * 0.055
    x0 = lx + inset
    x1 = lx + lw - inset
    x = x0 + (x1 - x0) * clamp(frac, 0.0, 1.0)
    u = 2.0 * clamp(frac, 0.0, 1.0) - 1.0
    rise = (g.lcd_spring_y - g.lcd_peak_y) * 0.92
    y = g.lcd_peak_y + 14 + rise * (u * u)
    return x, y


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
        try:
            fileno = sys.stdin.fileno()
        except (AttributeError, OSError, ValueError):
            return None
        while True:
            ready, _, _ = select.select([fileno], [], [], 0)
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
    """Non-blocking JSON lines from UART or a serial-like mock."""

    def __init__(self, port: str | object) -> None:
        from serial_reader import SerialLineReader, SerialUnavailable, open_serial

        if hasattr(port, "read"):
            ser = port
        else:
            try:
                ser = open_serial(str(port), baud=SERIAL_BAUD, timeout=0)
            except SerialUnavailable as e:
                print(f"serial: {e}", file=sys.stderr)
                raise SystemExit(2) from e
        self._reader = SerialLineReader(ser)

    def poll(self) -> Telemetry | None:
        return self._reader.poll()


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


def _italic_shear(pygame, img, shear: float = 0.14):
    """Lean glyphs right — AP1 tach numerals are a slightly italic gothic."""
    w, h = img.get_size()
    extra = max(1, int(h * shear))
    out = pygame.Surface((w + extra, h), pygame.SRCALPHA)
    for y in range(h):
        dx = int((h - 1 - y) * shear)
        out.blit(img, (dx, y), pygame.Rect(0, y, w, 1))
    return out


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


def cruise_telem() -> Telemetry:
    """Steady 80 km/h / 3000 r/min cruise used for the 05_cruise still."""
    t = sample_telem()
    t.rpm = 3000
    t.speed_kmh = 80.0
    t.fuel_pct = 48.0
    t.lamps = {**t.lamps, "turn_l": False, "high_beam": False}
    return t


def selftest_telem() -> Telemetry:
    """OEM bulb + LCD segment check — 188 / full bars / every telltale."""
    t = sample_telem()
    t.rpm = RPM_REDLINE
    t.speed_kmh = 188.0
    t.fuel_pct = 100.0
    t.ect_c = 105.0
    t.batt_v = 11.8
    t.lamps = {
        "oil": True,
        "cel": True,
        "abs": True,
        "turn_l": True,
        "turn_r": True,
        "high_beam": True,
        "fog": True,
        "fuel_low": True,
        "batt_warn": True,
        "ect_hot": True,
        "brake": True,
        "door": True,
        "srs": True,
        "seatbelt": True,
        "immobilizer": True,
        "maint": True,
        "eps": True,
    }
    return t


def arch_points(
    x0: float,
    x1: float,
    y_peak: float,
    y_spring: float,
    n: float = ARCH_N,
    steps: int = 56,
) -> list[tuple[int, int]]:
    """OEM lock: y = y_peak + rise * u²  (n is kept for call-site compatibility)."""
    del n
    rise = y_spring - y_peak
    pts: list[tuple[int, int]] = []
    for i in range(steps + 1):
        t = i / steps
        u = 2.0 * t - 1.0
        x = x0 + (x1 - x0) * t
        y = y_peak + rise * u * u
        pts.append((int(round(x)), int(round(y))))
    return pts


def hood_outer_points(g: FaceGeom = FACE) -> list[tuple[int, int]]:
    """Flat bottom, rectangular side notches (58–72%), parabolic crown (28% rise)."""
    mx, my, mw, mh = g.module
    step = g.step
    lx = mx + step
    rx = mx + mw - step
    pts: list[tuple[int, int]] = [
        (mx, my + mh),
        (mx + mw, my + mh),
        (mx + mw, g.notch_bot_y),
        (rx, g.notch_bot_y),
        (rx, g.notch_top_y),
        (rx, g.spring_y),
    ]
    pts.extend(arch_points(rx, lx, g.hood_peak_y, g.spring_y, n=g.arch_n))
    pts.extend(
        [
            (lx, g.spring_y),
            (lx, g.notch_top_y),
            (lx, g.notch_bot_y),
            (mx, g.notch_bot_y),
        ]
    )
    return pts


def lcd_aperture_points(g: FaceGeom = FACE) -> list[tuple[int, int]]:
    lx, ly, lw, lh = g.lcd
    rx = lx + lw
    bot = ly + lh
    pts: list[tuple[int, int]] = [(lx, bot), (rx, bot), (rx, g.lcd_spring_y)]
    pts.extend(arch_points(rx, lx, g.lcd_peak_y, g.lcd_spring_y, n=g.arch_n))
    pts.append((lx, g.lcd_spring_y))
    return pts


def hood_bottom_corners(g: FaceGeom = FACE) -> tuple[tuple[int, int], tuple[int, int]]:
    mx, my, mw, mh = g.module
    return (mx, my + mh), (mx + mw, my + mh)


def draw_cabin(pygame, surf) -> None:
    surf.fill(CABIN)


def draw_cowl(pygame, surf, sweep_t: float | None = None, g: FaceGeom = FACE) -> None:
    outer = hood_outer_points(g)
    pygame.draw.polygon(surf, COWL, outer)
    pygame.draw.polygon(surf, COWL_EDGE, outer, width=2)
    # Lip highlight along the outer arch only (still flat / orthographic)
    lip = arch_points(
        g.module[0] + g.step,
        g.module[0] + g.module[2] - g.step,
        g.hood_peak_y + 6,
        g.spring_y - 4,
        n=g.arch_n,
        steps=40,
    )
    if len(lip) > 1:
        pygame.draw.lines(surf, COWL_HIGH, False, lip, 3)

    aperture = lcd_aperture_points(g)
    pygame.draw.polygon(surf, WELL, aperture)
    pygame.draw.polygon(surf, LCD, aperture)
    # Night-idle amber wash so unlit ghosts sit on a warm LCD, not pure black
    wash = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(wash, (52, 34, 10, 38), aperture)
    surf.blit(wash, (0, 0))
    pygame.draw.polygon(surf, (22, 18, 14), aperture, width=2)

    if sweep_t is not None:
        band = arch_points(
            g.module[0] + g.step + 20,
            g.module[0] + g.module[2] - g.step - 20,
            g.hood_peak_y + 10,
            g.spring_y - 2,
            n=g.arch_n,
            steps=36,
        )
        t = clamp(sweep_t, 0.0, 1.0)
        i = int(t * max(0, len(band) - 8))
        chunk = band[i : i + 8]
        if len(chunk) > 1:
            pygame.draw.lines(surf, lerp_colour(AMBER, WHITE, t), False, chunk, 8)


def _expand_poly(pts: list[tuple[int, int]], px: float) -> list[tuple[int, int]]:
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out: list[tuple[int, int]] = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        n = math.hypot(dx, dy) or 1.0
        out.append((int(x + dx / n * px), int(y + dy / n * px)))
    return out


def _blit_seg_bloom(pygame, surf, bloom, pts, color) -> None:
    glow = (
        min(255, color[0] + 28),
        min(255, color[1] + 20),
        min(255, color[2] + 8),
        78,
    )
    pygame.draw.polygon(bloom, glow, _expand_poly(pts, 5))
    pygame.draw.polygon(surf, color, pts)


def _tick_poly(x: float, y: float, w: float, h: float) -> list[tuple[int, int]]:
    """Vertical LCD tick hanging down from the arch."""
    hw = w * 0.5
    return [
        (int(x - hw), int(y)),
        (int(x + hw), int(y)),
        (int(x + hw), int(y + h)),
        (int(x - hw), int(y + h)),
    ]


def draw_tach_segments(
    pygame,
    surf,
    lit_frac: float,
    ghost: bool = True,
    g: FaceGeom = FACE,
) -> None:
    """OEM ticks along the parabola: majors each 1000, minors each 200, five redline blocks 8–9."""
    red_from = 8.0 / 9.0
    bloom = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    n_minor = 9 * TACH_MINORS_PER  # 36 × 200 r/min steps across 0–9

    # Faint amber wash under the scale (night-idle backlight)
    for i in range(40):
        frac = i / 39.0
        x, y = tach_arch_xy(frac, g)
        h = 36 if 0.08 < frac < 0.92 else 26
        pygame.draw.rect(surf, AMBER_WASH, pygame.Rect(int(x - 5), int(y + 2), 10, h))

    for i in range(n_minor + 1):
        frac = i / n_minor
        x, y = tach_arch_xy(frac, g)
        major = i % TACH_MINORS_PER == 0
        in_red = frac >= red_from - 1e-6
        on = frac <= lit_frac + 1e-6
        if in_red:
            continue
        # 0–1 shorter/thinner; 1–8 longer majors
        if frac <= 1.0 / 9.0 + 1e-6:
            w, h = (5, 28) if major else (3, 18)
        else:
            w, h = (7, 40) if major else (4, 26)
        pts = _tick_poly(x, y + 4, w, h)
        if on:
            col = WHITE if major else lerp_colour(AMBER, AMBER_HOT, frac)
            _blit_seg_bloom(pygame, surf, bloom, pts, col)
        elif ghost:
            pygame.draw.polygon(surf, AMBER_GHOST if not major else (58, 48, 36), pts)

    # Five thick orange-red blocks 8–9 (OEM redline)
    for i in range(REDLINE_BLOCKS):
        t0 = red_from + (1.0 - red_from) * (i / REDLINE_BLOCKS)
        t1 = red_from + (1.0 - red_from) * ((i + 1) / REDLINE_BLOCKS)
        mid = (t0 + t1) * 0.5
        x, y = tach_arch_xy(mid, g)
        on = mid <= lit_frac + 1e-6
        pts = _tick_poly(x, y - 2, 16, 52)
        if on:
            _blit_seg_bloom(pygame, surf, bloom, pts, ORANGE if i < 4 else RED)
        else:
            pygame.draw.polygon(surf, RED_GHOST if ghost else (36, 12, 10), pts)

    small = pygame.transform.smoothscale(bloom, (surf.get_width() // 3, surf.get_height() // 3))
    surf.blit(pygame.transform.smoothscale(small, surf.get_size()), (0, 0))

    # Leading-edge pointer (OEM orange triangle on the live tick)
    tip_frac = clamp(lit_frac, 0.0, 1.0)
    tx, ty = tach_arch_xy(tip_frac, g)
    tri = [(int(tx), int(ty - 2)), (int(tx - 7), int(ty - 14)), (int(tx + 7), int(ty - 14))]
    pygame.draw.polygon(surf, AMBER_HOT if tip_frac < red_from else RED, tri)


def draw_tach_numbers(pygame, fonts, surf, dim: bool = False, g: FaceGeom = FACE) -> None:
    for i in range(10):
        hot = i >= 8
        col = (RED if hot else AMBER) if not dim else (RED_DIM if hot else AMBER_DIM)
        frac = i / 9.0
        x, y = tach_arch_xy(frac, g)
        # Numerals sit just inside / below the ticks
        pos = (int(x), int(y + (58 if i not in (0, 9) else 44)))
        if i == 0:
            pos = (pos[0] + 8, pos[1] + 8)
        elif i == 9:
            pos = (pos[0] - 6, pos[1] + 8)
        img = _italic_shear(pygame, fonts["tick"].render(str(i), True, col), 0.12)
        surf.blit(img, img.get_rect(center=pos))
    lx, ly = tach_arch_xy(0.03, g)
    blit_text(
        surf,
        fonts["micro"],
        "x1000r/min",
        DIM if not dim else MUTED,
        (int(lx + 36), int(ly + 78)),
        "center",
    )


def _seg_bar(
    pygame,
    surf,
    rect: tuple[int, int, int, int],
    frac: float,
    segs: int,
    warn_low: bool,
    hot_end: bool,
) -> None:
    x, y, w, h = rect
    pygame.draw.line(surf, AMBER_DIM, (x, y + h + 2), (x + w, y + h + 2), 2)
    gap = 2
    seg_w = (w - gap * (segs - 1)) / segs
    lit = int(round(frac * segs))
    for i in range(segs):
        sx = x + i * (seg_w + gap)
        on = i < lit
        last = i >= segs - 1
        if on and ((warn_low and i == 0) or (hot_end and last and frac > 0.92)):
            col = RED
        elif on:
            col = AMBER
        elif warn_low and i == 0:
            col = RED_DIM
        else:
            col = AMBER_GHOST
        pygame.draw.rect(surf, col, pygame.Rect(int(sx), y, max(3, int(seg_w)), h), border_radius=1)


def _thermometer_icon(pygame, surf, cx: int, cy: int, col) -> None:
    """AP1 TEMP pictogram: stem, bulb, right-hand ticks, three waves below."""
    pygame.draw.rect(surf, col, pygame.Rect(cx - 2, cy - 16, 5, 18), border_radius=2)
    pygame.draw.circle(surf, col, (cx, cy + 6), 6)
    for dy in (-12, -7, -2, 3):
        pygame.draw.line(surf, col, (cx + 5, cy + dy), (cx + 11, cy + dy), 2)
    for i, y in enumerate((cy + 14, cy + 18, cy + 22)):
        pts = [(cx - 8 + x, y + (2 if (x // 4) % 2 else -2)) for x in range(0, 20, 4)]
        if len(pts) >= 2:
            pygame.draw.lines(surf, col, False, pts, 2)


def _pump_icon(pygame, surf, cx: int, cy: int, col) -> None:
    """AP1 FUEL pictogram: pump body, window, hose loop, nozzle."""
    pygame.draw.rect(surf, col, pygame.Rect(cx - 9, cy - 8, 11, 18), border_radius=1)
    pygame.draw.rect(surf, col, pygame.Rect(cx - 7, cy - 14, 7, 6), border_radius=1)
    pygame.draw.rect(surf, (0, 0, 0), pygame.Rect(cx - 6, cy - 5, 5, 4))
    pygame.draw.arc(surf, col, pygame.Rect(cx - 2, cy - 8, 16, 16), -0.4, 1.6, 2)
    pygame.draw.rect(surf, col, pygame.Rect(cx + 10, cy - 2, 4, 10), border_radius=1)


def draw_temp_bar(pygame, fonts, surf, frac: float, hot: bool, g: FaceGeom = FACE) -> None:
    """Horizontal TEMP C–H at the bottom-left of the LCD (OEM)."""
    x, y, w, h = g.temp
    blit_text(surf, fonts["tiny"], "C", AMBER, (x - 14, y + h // 2), "center")
    blit_text(surf, fonts["tiny"], "H", RED if hot else AMBER, (x + w + 14, y + h // 2), "center")
    _thermometer_icon(pygame, surf, x + 10, y - 22, AMBER if not hot else RED)
    _seg_bar(pygame, surf, g.temp, frac, TEMP_SEGS, warn_low=False, hot_end=hot)


def draw_fuel_bar(pygame, fonts, surf, frac: float, low: bool, g: FaceGeom = FACE) -> None:
    """Horizontal FUEL E–F at the bottom-right of the LCD, mirrored with TEMP."""
    x, y, w, h = g.fuel
    blit_text(surf, fonts["tiny"], "E", RED if low else AMBER, (x - 14, y + h // 2), "center")
    blit_text(surf, fonts["tiny"], "F", AMBER, (x + w + 14, y + h // 2), "center")
    _pump_icon(pygame, surf, x + w - 6, y - 20, AMBER if not low else ORANGE)
    _seg_bar(pygame, surf, g.fuel, frac, FUEL_SEGS, warn_low=low, hot_end=False)


def draw_speed(pygame, fonts, surf, speed: float, g: FaceGeom = FACE) -> None:
    """3-digit 7-seg speed in a rectangular LCD well. Ghost is the OEM 188."""
    value = int(round(clamp(speed, 0.0, 399.0)))
    digits = f"{value:d}".rjust(3)
    cx, cy = g.speed_c
    win = (cx - 210, cy - 78, 360, 150)
    lcd_window(pygame, surf, win, (14, 9, 4), (48, 32, 12))
    box = blit_digits(
        pygame,
        surf,
        digits,
        (cx - 24, cy),
        digit_h=118,
        color=AMBER_HOT,
        ghost=AMBER_GHOST,
        ghost_text="188",
        bloom=True,
        italic=0.05,
    )
    unit_x = box[0] + box[2] + 18
    blit_text(surf, fonts["label"], "km/h", AMBER, (unit_x, cy - 12), "midleft")
    blit_text(surf, fonts["micro"], "mph", DIM, (unit_x, cy + 16), "midleft")


def draw_odo_row(pygame, fonts, surf, face: DisplayState, batt_warn: bool, g: FaceGeom = FACE) -> None:
    """6-digit odo + xxx.x trip in a smaller LCD well under the speed."""
    cx, y = g.odo_c
    odo = int(round(face.odo_km)) % 1_000_000
    trip = clamp(face.trip_km, 0.0, 999.9)
    win = (cx - 230, y - 36, 460, 72)
    lcd_window(pygame, surf, win, (12, 8, 4), (42, 28, 10))
    blit_text(surf, fonts["micro"], "ODO", DIM, (cx - 210, y - 14), "midleft")
    blit_digits(
        pygame,
        surf,
        f"{odo:06d}",
        (cx - 70, y + 10),
        digit_h=28,
        color=AMBER,
        ghost=AMBER_GHOST,
        ghost_text="888888",
        bloom=True,
        italic=0.03,
    )
    blit_text(surf, fonts["micro"], "TRIP A", DIM, (cx + 70, y - 14), "midleft")
    blit_digits(
        pygame,
        surf,
        f"{trip:05.1f}",
        (cx + 150, y + 10),
        digit_h=28,
        color=AMBER,
        ghost=AMBER_GHOST,
        ghost_text="888.8",
        bloom=True,
        italic=0.03,
    )
    blit_text(
        surf,
        fonts["micro"],
        f"{face.batt_v:.1f}V",
        RED if batt_warn else DIM,
        (cx + 232, y - 14),
        "midleft",
    )


def _round_btn(pygame, fonts, surf, rect, left: str, right: str | None = None) -> None:
    """Circular OEM bezel button (or a joined −/+ pair)."""
    x, y, w, h = rect
    if right is None:
        pygame.draw.ellipse(surf, BEZEL_BTN, pygame.Rect(x, y, w, h))
        pygame.draw.ellipse(surf, (88, 88, 86), pygame.Rect(x, y, w, h), width=1)
        blit_text(surf, fonts["lamp"], left, WHITE, (x + w // 2, y + h // 2), "center")
        return
    # Two circles sharing a rocker span
    r = h // 2
    pygame.draw.circle(surf, BEZEL_BTN, (x + r, y + r), r)
    pygame.draw.circle(surf, BEZEL_BTN, (x + w - r, y + r), r)
    pygame.draw.rect(surf, BEZEL_BTN, pygame.Rect(x + r, y, w - 2 * r, h))
    pygame.draw.line(surf, (72, 72, 70), (x + w // 2, y + 5), (x + w // 2, y + h - 5), 2)
    blit_text(surf, fonts["tiny"], left, RED, (x + w * 0.25, y + h // 2), "center")
    blit_text(surf, fonts["tiny"], right, WHITE, (x + w * 0.75, y + h // 2), "center")


def _cruise_cancel_icon(pygame, surf, cx: int, cy: int, col) -> None:
    """OEM PUSH CANCEL: speedo dial, needle to 2 o'clock, cancel X."""
    pygame.draw.circle(surf, col, (cx, cy), 8, 2)
    pygame.draw.circle(surf, col, (cx, cy), 2)
    pygame.draw.line(surf, col, (cx, cy), (cx + 5, cy - 5), 2)
    for ang in (3.6, 2.8, 2.2, 1.55):
        x0 = cx + int(5.2 * math.cos(ang))
        y0 = cy - int(5.2 * math.sin(ang))
        x1 = cx + int(7.6 * math.cos(ang))
        y1 = cy - int(7.6 * math.sin(ang))
        pygame.draw.line(surf, col, (x0, y0), (x1, y1), 2)
    pygame.draw.line(surf, col, (cx + 8, cy + 2), (cx + 14, cy + 8), 2)
    pygame.draw.line(surf, col, (cx + 14, cy + 2), (cx + 8, cy + 8), 2)


def draw_hardware_strip(
    pygame,
    fonts,
    surf,
    face: DisplayState,
    bulb_check: bool = False,
    g: FaceGeom = FACE,
) -> None:
    """Lower bezel: circular −/+, telltales on the face, SEL + TRIP, mph·km/h."""
    _round_btn(pygame, fonts, surf, g.rocker, "−", "+")

    rx, ry, rw, rh = g.rocker
    dial_x = rx + 14
    dial_y = ry + rh + 16
    _cruise_cancel_icon(pygame, surf, dial_x, dial_y, WHITE)
    blit_text(surf, fonts["lamp"], "PUSH CANCEL", WHITE, (dial_x + 78, dial_y), "center")

    bx, by, bw, bh = g.lamp_band
    lamps = lamp_states(
        face.lamps,
        bulb_check=bulb_check,
        batt_low=face.batt_v < BATT_LOW_V,
    )
    total = sum(item.width for item in lamps)
    x = bx + max(8, (bw - total) // 2)
    cy = by + bh // 2
    icon_h = max(22, bh - 10)
    for item in lamps:
        cx = x + item.width // 2
        col = item.color if item.lit else LAMP_GHOST
        sprite = icon_surface(pygame, item.kind, col, icon_h, max_width=item.width - 4)
        if item.lit:
            blit_glow(pygame, surf, sprite, (cx, cy), strength=0.38, scale=1.08)
        else:
            surf.blit(sprite, sprite.get_rect(center=(cx, cy)))
        x += item.width

    _round_btn(pygame, fonts, surf, g.trip_blank, "SEL")
    _round_btn(pygame, fonts, surf, g.trip, "TRIP")
    tx, ty, tw, th = g.trip
    blit_text(
        surf,
        fonts["micro"],
        "mph · km/h",
        WHITE,
        (tx + tw // 2, ty + th + 16),
        "center",
    )


def draw_ready_card(fonts, surf, face: DisplayState, g: FaceGeom = FACE) -> None:
    """ID.4-like pre-drive summary sitting in the LCD well."""
    cx = g.speed_c[0]
    ly = g.lcd[1]
    blit_text(surf, fonts["micro"], "HONDA  S2000  AP1", DIM, (cx, ly + 70), "center")
    blit_text(surf, fonts["ready"], "READY", AMBER, g.speed_c, "center")
    blit_text(surf, fonts["tiny"], "IGNITION ON  ·  SYSTEMS OK", DIM, (cx, g.speed_c[1] + 58), "center")
    chips = [
        ("BATT", f"{face.batt_v:.1f} V"),
        ("FUEL", f"{face.fuel_pct:.0f} %"),
        ("TEMP", f"{face.ect_c:.0f} °C"),
        ("ODO", f"{face.odo_km:,.0f} km"),
    ]
    y = g.temp[1] - 8
    x0 = cx - 270
    for i, (name, val) in enumerate(chips):
        x = x0 + i * 180
        blit_text(surf, fonts["micro"], name, DIM, (x, y), "center")
        blit_text(surf, fonts["readout"], val, AMBER, (x, y + 26), "center")


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
    draw_tach_numbers(pygame, fonts, layer)
    draw_temp_bar(pygame, fonts, layer, ect_frac(face.ect_c), face.ect_c >= ECT_HOT_C)
    draw_fuel_bar(pygame, fonts, layer, fuel_frac(face.fuel_pct), face.fuel_pct < FUEL_LOW_PCT)
    draw_speed(pygame, fonts, layer, face.speed_kmh)
    draw_odo_row(
        pygame,
        fonts,
        layer,
        face,
        face.batt_v < BATT_LOW_V or face.lamps.get("batt_warn", False),
    )
    draw_hardware_strip(pygame, fonts, layer, face, bulb_check=bulb_check)
    if fade < 0.999:
        layer.set_alpha(int(255 * clamp(fade, 0.0, 1.0)))
        surf.blit(layer, (0, 0))


def draw_caption(fonts, surf, g: FaceGeom = FACE) -> None:
    mx, my, mw, mh = g.module
    blit_text(
        surf,
        fonts["micro"],
        "OEM cluster remains powered for legal odometer  ·  Esc quit",
        MUTED,
        (W // 2, my + mh + 28),
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
        draw_tach_segments(pygame, surf, 0.0, ghost=True)
        draw_tach_numbers(pygame, fonts, surf, dim=True)
        draw_temp_bar(pygame, fonts, surf, 0.0, False)
        draw_fuel_bar(pygame, fonts, surf, 0.0, False)
        draw_hardware_strip(pygame, fonts, surf, face, bulb_check=False)
    elif phase == "ready":
        draw_ready_card(fonts, surf, face)
        draw_hardware_strip(pygame, fonts, surf, face, bulb_check=False)
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


# Headless smoke walks the boot clock so CI covers sweep → ready → reveal → live
SMOKE_PHASES: tuple[tuple[str, float], ...] = (
    ("sweep", 0.55),
    ("ready", 0.55),
    ("reveal", 0.40),
    ("live", 1.0),
)

SCREENSHOT_SCENES: tuple[tuple[str, str, float], ...] = (
    ("01_sweep", "sweep", 0.55),
    ("02_ready", "ready", 0.55),
    ("03_reveal", "reveal", 0.40),
    ("04_live", "live", 1.0),
    ("05_cruise", "live", 1.0),
)


def write_screenshots(pygame, fonts, face: DisplayState, dest: Path) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    canvas = pygame.Surface((W, H))
    cruise = DisplayState()
    cruise.snap(cruise_telem())
    cruise.trip_origin = cruise.odo_km - 128.4
    cruise.trip_km = 128.4
    for name, phase, local_t in SCREENSHOT_SCENES:
        draw_frame(pygame, fonts, canvas, cruise if name.endswith("cruise") else face, phase, local_t)
        path = dest / f"{name}.png"
        pygame.image.save(canvas, str(path))
        written.append(path)
    return written


def build_fonts(pygame) -> dict:
    return {
        "speed": _font(pygame, 132, bold=True, mono=True),
        "ready": _font(pygame, 78, bold=True),
        "tick": _font(pygame, 26, bold=True),
        "label": _font(pygame, 22),
        "readout": _font(pygame, 26, bold=True, mono=True),
        "tiny": _font(pygame, 18, bold=True),
        "micro": _font(pygame, 15),
        "lamp": _font(pygame, 14, bold=True),
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
        print("pygame is required: uv sync   (or pip install -r requirements.txt)", file=sys.stderr)
        raise SystemExit(1)

    pygame, screen = init_pygame(args.windowed, headless=args.smoke)
    fonts = build_fonts(pygame)
    clock = pygame.time.Clock()

    if args.serial:
        source: StdinSource | SerialSource = SerialSource(args.serial)
    else:
        source = StdinSource()

    telem = sample_telem() if args.smoke else Telemetry()
    incoming = source.poll()
    if incoming is not None:
        telem = incoming

    face = DisplayState()
    face.snap(telem)
    if args.smoke:
        face.trip_origin = telem.odo_km - 128.4
        face.trip_km = 128.4

    if args.screenshot:
        paths = write_screenshots(pygame, fonts, face, Path(args.screenshot))
        for path in paths:
            print(path)

    if args.smoke:
        for phase, local_t in SMOKE_PHASES:
            draw_frame(pygame, fonts, screen, face, phase, local_t)
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
