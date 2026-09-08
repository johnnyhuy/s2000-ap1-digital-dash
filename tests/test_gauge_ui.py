"""OEM cluster helpers — flags, lerp, intro phases, smoke path."""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gauge_ui import (  # noqa: E402
    ARCH_RISE_PCT,
    FACE,
    LAMP_AMBER,
    LAMP_BLUE,
    LAMP_GREEN,
    LAMP_RED,
    MODULE_ASPECT,
    NOTCH_BOT_PCT,
    NOTCH_TOP_PCT,
    REDLINE_BLOCKS,
    DisplayState,
    PHASE_READY_S,
    PHASE_REVEAL_S,
    PHASE_SWEEP_S,
    RPM_REDLINE,
    _lamp_spec,
    ect_frac,
    exp_smooth,
    fuel_frac,
    hood_bottom_corners,
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
        args = parse_args(["--windowed", "--screenshot", "shots", "--serial", "--gif", "out.gif"])
        self.assertTrue(args.windowed)
        self.assertEqual(args.screenshot, "shots")
        self.assertEqual(args.serial, "/dev/ttyUSB0")
        self.assertEqual(args.gif, "out.gif")


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
                [
                    "01_sweep.png",
                    "02_ready.png",
                    "03_reveal.png",
                    "04_live.png",
                    "05_cruise.png",
                ],
            )


class FaceGeomTests(unittest.TestCase):
    def test_temp_and_fuel_are_horizontal_bottom_bars(self) -> None:
        tx, ty, tw, th = FACE.temp
        fx, fy, fw, fh = FACE.fuel
        self.assertEqual(ty, fy)
        self.assertEqual(th, fh)
        self.assertGreater(tw, th * 3)
        self.assertGreater(fw, fh * 3)
        self.assertLess(tx + tw, FACE.speed_c[0])
        self.assertGreater(fx, FACE.speed_c[0])
        lcd_bottom = FACE.lcd[1] + FACE.lcd[3]
        self.assertGreater(ty, FACE.lcd[1] + FACE.lcd[3] * 0.75)
        self.assertLessEqual(ty + th, lcd_bottom + 2)

    def test_module_is_flat_bottom_and_stepped(self) -> None:
        bl, br = hood_bottom_corners(FACE)
        self.assertEqual(bl[1], br[1])
        self.assertGreater(FACE.step, 0)
        self.assertGreater(FACE.lcd[0], FACE.module[0])
        self.assertLess(FACE.lcd[0] + FACE.lcd[2], FACE.module[0] + FACE.module[2])

    def test_bezel_sits_below_lcd(self) -> None:
        lcd_bottom = FACE.lcd[1] + FACE.lcd[3]
        self.assertGreaterEqual(FACE.bezel[1], lcd_bottom)

    def test_module_aspect_is_locked(self) -> None:
        self.assertAlmostEqual(MODULE_ASPECT, 2.35, places=2)
        mw, mh = FACE.module[2], FACE.module[3]
        self.assertAlmostEqual(mw / mh, 2.35, delta=0.05)

    def test_lcd_is_wide_and_short(self) -> None:
        aspect = FACE.lcd[2] / FACE.lcd[3]
        self.assertGreater(aspect, 2.8)
        self.assertLess(aspect, 4.2)

    def test_locked_bottom_and_speed_percentages(self) -> None:
        mx, my, mw, mh = FACE.module
        self.assertAlmostEqual((FACE.temp[0] - mx) / mw, 0.075, delta=0.01)
        self.assertAlmostEqual((FACE.temp[1] - my) / mh, 0.72, delta=0.015)
        self.assertAlmostEqual((FACE.fuel[0] - mx) / mw, 0.745, delta=0.01)
        self.assertAlmostEqual((FACE.speed_c[0] - mx) / mw, 0.50, delta=0.01)
        self.assertAlmostEqual((FACE.speed_c[1] - my) / mh, 0.40, delta=0.02)
        self.assertAlmostEqual((FACE.bezel[1] - my) / mh, 0.805, delta=0.02)

    def test_five_redline_blocks(self) -> None:
        self.assertEqual(REDLINE_BLOCKS, 5)

    def test_lamp_colours_match_lit_notes(self) -> None:
        face = DisplayState()
        by_kind = {k: c for k, _on, c in _lamp_spec(face, bulb_check=True)}
        for kind in ("brake", "bat", "oil", "door", "seat", "srs"):
            self.assertEqual(by_kind[kind], LAMP_RED, kind)
        for kind in ("abs", "cel", "maint", "eps"):
            self.assertEqual(by_kind[kind], LAMP_AMBER, kind)
        for kind in ("turn_l", "turn_r", "key"):
            self.assertEqual(by_kind[kind], LAMP_GREEN, kind)
        self.assertEqual(by_kind["hi"], LAMP_BLUE)

    def test_notch_and_arch_lock(self) -> None:
        mx, my, mw, mh = FACE.module
        self.assertAlmostEqual(NOTCH_TOP_PCT, 0.58)
        self.assertAlmostEqual(NOTCH_BOT_PCT, 0.72)
        self.assertAlmostEqual(ARCH_RISE_PCT, 0.28)
        self.assertAlmostEqual((FACE.notch_top_y - my) / mh, 0.58, delta=0.015)
        self.assertAlmostEqual((FACE.notch_bot_y - my) / mh, 0.72, delta=0.015)
        self.assertAlmostEqual((FACE.spring_y - my) / mh, 0.28, delta=0.02)
        self.assertEqual(FACE.hood_peak_y, my)


if __name__ == "__main__":
    unittest.main()
