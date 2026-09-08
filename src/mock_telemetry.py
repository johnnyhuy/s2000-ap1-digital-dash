#!/usr/bin/env python3
"""Emit fake driving telemetry as newline JSON on stdout @ 20 Hz.

Pipe into the gauge UI:
  python mock_telemetry.py | python gauge_ui.py
"""
from __future__ import annotations

import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocol import MOCK_HZ, Telemetry


def driving_loop(t: float, odo: float) -> Telemetry:
    """Synthetic drive: idle → cruise → VTEC blip → coast."""
    pull = 0.5 + 0.5 * math.sin(t * 0.25)
    rpm = int(1800 + 4200 * pull + 1800 * max(0.0, math.sin(t * 0.55)) ** 2)
    rpm = max(850, min(9200, rpm))

    speed = max(0.0, 35 + 95 * pull + 25 * math.sin(t * 0.18))
    fuel = max(8.0, 62.0 - (t * 0.02) % 40.0)
    ect = 82.0 + 12.0 * (1.0 - math.exp(-t / 45.0)) + 3.0 * math.sin(t * 0.08)
    batt = 14.1 - 0.4 * (1.0 if rpm < 1000 else 0.0) + 0.15 * math.sin(t * 0.3)

    # Blinkers: left blink for a few seconds every ~16 s
    blink_phase = (t % 16.0) < 3.2
    blink_on = blink_phase and (int(t * 2.4) % 2 == 0)

    lamps = {
        "oil": rpm < 700,  # never in mock, but keep key
        "cel": False,
        "abs": False,
        "turn_l": blink_on,
        "turn_r": False,
        "high_beam": (int(t) // 20) % 5 == 0,
        "fog": False,
        "fuel_low": fuel < 15.0,
        "batt_warn": batt < 12.2,
        "ect_hot": ect > 105.0,
    }

    return Telemetry(
        rpm=rpm,
        speed_kmh=round(speed, 1),
        fuel_pct=round(fuel, 1),
        ect_c=round(ect, 1),
        batt_v=round(batt, 2),
        odo_km=round(odo, 1),
        lamps=lamps,
    )


def main() -> None:
    dt = 1.0 / MOCK_HZ
    t0 = time.monotonic()
    odo = 142_857.3  # cheeky starting odo (display-only; OEM cluster stays legal)
    try:
        while True:
            now = time.monotonic()
            t = now - t0
            telem = driving_loop(t, odo)
            odo += telem.speed_kmh / 3600.0 * dt
            telem.odo_km = round(odo, 1)
            sys.stdout.write(telem.to_line())
            sys.stdout.flush()
            sleep_for = dt - (time.monotonic() - now)
            if sleep_for > 0:
                time.sleep(sleep_for)
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
