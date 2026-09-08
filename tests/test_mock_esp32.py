"""Mock ESP32 UART emitter — same frozen JSON as Phase 2 would send."""
from __future__ import annotations

import io
import subprocess
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))

from mocks.esp32_uart import (  # noqa: E402
    OEM_EXTRA_LAMPS,
    emit_frames,
    frame_at,
    iter_frames,
    parse_args,
    warn_frame,
)
from protocol import MOCK_HZ, REQUIRED_FIELDS, parse_line  # noqa: E402


class EmitterUnitTests(unittest.TestCase):
    def test_drive_frames_are_protocol_valid(self) -> None:
        frames = list(iter_frames(8, scenario="drive", hz=MOCK_HZ))
        self.assertEqual(len(frames), 8)
        for telem in frames:
            parsed = parse_line(telem.to_line())
            for key in REQUIRED_FIELDS:
                self.assertIn(key, parsed.to_dict())
            for extra in OEM_EXTRA_LAMPS:
                self.assertIn(extra, parsed.lamps)

    def test_warn_scenario_lights_oem_extras(self) -> None:
        telem = warn_frame()
        parsed = parse_line(telem.to_line())
        self.assertLess(parsed.fuel_pct, 15.0)
        self.assertGreater(parsed.ect_c, 105.0)
        self.assertLess(parsed.batt_v, 12.2)
        for extra in OEM_EXTRA_LAMPS:
            self.assertTrue(parsed.lamp(extra), extra)
        self.assertTrue(parsed.lamp("high_beam"))
        self.assertTrue(parsed.lamp("fuel_low"))

    def test_idle_is_parked(self) -> None:
        telem = frame_at(0.0, 10.0, "idle")
        self.assertEqual(telem.speed_kmh, 0.0)
        self.assertFalse(any(telem.lamps.values()))

    def test_emit_frames_writes_newline_json(self) -> None:
        buf = io.StringIO()
        n = emit_frames(iter_frames(3, scenario="idle"), buf)
        self.assertEqual(n, 3)
        lines = [ln for ln in buf.getvalue().splitlines() if ln]
        self.assertEqual(len(lines), 3)
        self.assertEqual(parse_line(lines[0]).rpm, 850)

    def test_cli_flags(self) -> None:
        args = parse_args(["--count", "20", "--immediate", "--scenario", "warn"])
        self.assertEqual(args.count, 20)
        self.assertTrue(args.immediate)
        self.assertEqual(args.scenario, "warn")
        self.assertEqual(args.hz, MOCK_HZ)


class EmitterCliTests(unittest.TestCase):
    def test_module_emits_immediate_frames(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                "-m",
                "mocks.esp32_uart",
                "--count",
                "5",
                "--immediate",
                "--scenario",
                "drive",
            ],
            cwd=_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        lines = [ln for ln in proc.stdout.splitlines() if ln]
        self.assertEqual(len(lines), 5)
        parsed = parse_line(lines[-1])
        for key in REQUIRED_FIELDS:
            self.assertIn(key, parsed.to_dict())


if __name__ == "__main__":
    unittest.main()
