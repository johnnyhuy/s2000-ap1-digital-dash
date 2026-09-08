"""Mock drive loop must emit the Phase 1 JSON field names."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mock_telemetry import driving_loop  # noqa: E402
from protocol import REQUIRED_FIELDS, parse_line  # noqa: E402


class MockTelemetryTests(unittest.TestCase):
    def test_driving_loop_round_trips(self) -> None:
        telem = driving_loop(12.0, 1000.0)
        parsed = parse_line(telem.to_line())
        for key in REQUIRED_FIELDS:
            self.assertIn(key, parsed.to_dict())
        self.assertGreaterEqual(parsed.rpm, 850)
        self.assertGreaterEqual(parsed.speed_kmh, 0.0)
        self.assertTrue(0.0 <= parsed.fuel_pct <= 100.0)
        self.assertIn("turn_l", parsed.lamps)
