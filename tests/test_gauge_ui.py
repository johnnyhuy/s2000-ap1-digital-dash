"""OEM cluster helpers — flags, lerp, intro phases, smoke path."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gauge_ui import (  # noqa: E402
    DisplayState,
    PHASE_READY_S,
    PHASE_REVEAL_S,
    PHASE_SWEEP_S,
    RPM_REDLINE,
    ect_frac,
    exp_smooth,
    fuel_frac,
    intro_duration_s,
    intro_phase_at,
    lerp,
    parse_args,
    reveal_rpm,
    sample_telem,
)
from protocol import REQUIRED_FIELDS, parse_line  # noqa: E402


class FlagTests(unittest.TestCase):
    def test_smoke_defaults_skip_intro(self) -> None:
        args = parse_args(["--smoke"])
        self.assertTrue(args.smoke)
        self.assertFalse(args.intro)

    def test_intro_and_no_intro(self) -> None:
        self.assertTrue(parse_args(["--intro"]).intro)
        self.assertFalse(parse_args(["--no-intro"]).intro)

    def test_screenshot_and_windowed_and_serial(self) -> None:
        args = parse_args(["--windowed", "--screenshot", "shots", "--serial"])
        self.assertTrue(args.windowed)
        self.assertEqual(args.screenshot, "shots")
        self.assertEqual(args.serial, "/dev/ttyUSB0")


class IntroTests(unittest.TestCase):
    def test_phase_order(self) -> None:
        self.assertEqual(intro_phase_at(0.0)[0], "sweep")
        self.assertEqual(intro_phase_at(PHASE_SWEEP_S + 0.01)[0], "ready")
        self.assertEqual(
            intro_phase_at(PHASE_SWEEP_S + PHASE_READY_S + 0.01)[0], "reveal"
        )
        self.assertEqual(intro_phase_at(intro_duration_s() + 0.2)[0], "live")

    def test_reveal_rpm_hits_redline_then_settles(self) -> None:
        self.assertAlmostEqual(reveal_rpm(0.0, 2000), 0.0)
        self.assertGreater(reveal_rpm(0.3, 2000), 3000)
        self.assertAlmostEqual(reveal_rpm(0.58, 2000), float(RPM_REDLINE))
        self.assertAlmostEqual(reveal_rpm(1.0, 2000), 2000.0)


class LerpTests(unittest.TestCase):
    def test_exp_smooth_approaches_target(self) -> None:
        v = 0.0
        for _ in range(40):
            v = exp_smooth(v, 100.0, 0.016, 0.08)
        self.assertGreater(v, 95.0)

    def test_lerp_midpoint(self) -> None:
        self.assertAlmostEqual(lerp(0.0, 10.0, 0.5), 5.0)

    def test_fracs(self) -> None:
        self.assertEqual(ect_frac(40.0), 0.0)
        self.assertEqual(ect_frac(105.0), 1.0)
        self.assertEqual(fuel_frac(50.0), 0.5)
        self.assertEqual(fuel_frac(140.0), 1.0)


class DisplayStateTests(unittest.TestCase):
    def test_sample_keeps_protocol_fields(self) -> None:
        telem = sample_telem()
        parsed = parse_line(telem.to_line())
        for key in REQUIRED_FIELDS:
            self.assertIn(key, parsed.to_dict())

    def test_follow_snaps_lamps_and_tracks_trip(self) -> None:
        face = DisplayState()
        telem = sample_telem()
        face.snap(telem)
        face.trip_origin = telem.odo_km - 12.5
        face.follow(telem, 0.016)
        self.assertTrue(face.lamps["turn_l"])
        self.assertAlmostEqual(face.trip_km, 12.5, places=1)


class SmokeTests(unittest.TestCase):
    def test_smoke_writes_named_shots(self) -> None:
        from gauge_ui import main

        with tempfile.TemporaryDirectory() as tmp:
            main(["--smoke", "--screenshot", tmp])
            self.assertEqual(
                sorted(os.listdir(tmp)),
                ["01_sweep.png", "02_ready.png", "03_reveal.png", "04_live.png"],
            )


if __name__ == "__main__":
    unittest.main()
