"""Protocol parse/validate — keep Honda/Abby JSON field names stable."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from protocol import (  # noqa: E402
    ProtocolError,
    REQUIRED_FIELDS,
    Telemetry,
    parse_line,
    try_parse_line,
    validate,
)


class ProtocolTests(unittest.TestCase):
    def test_required_field_names(self) -> None:
        self.assertEqual(
            REQUIRED_FIELDS,
            ("rpm", "speed_kmh", "fuel_pct", "ect_c", "batt_v", "odo_km"),
        )

    def test_round_trip_line(self) -> None:
        telem = Telemetry(
            rpm=6500,
            speed_kmh=97.5,
            fuel_pct=40.0,
            ect_c=88.0,
            batt_v=14.1,
            odo_km=1234.5,
            lamps={"turn_l": True, "oil": False},
        )
        parsed = parse_line(telem.to_line())
        self.assertEqual(parsed.rpm, 6500)
        self.assertAlmostEqual(parsed.speed_kmh, 97.5)
        self.assertTrue(parsed.lamp("turn_l"))
        self.assertFalse(parsed.lamp("oil"))

    def test_missing_field_raises(self) -> None:
        payload = {
            "rpm": 1,
            "speed_kmh": 0,
            "fuel_pct": 50,
            "ect_c": 80,
            "batt_v": 12.6,
        }
        with self.assertRaises(ProtocolError):
            validate(payload)

    def test_fuel_clamped(self) -> None:
        data = validate(
            {
                "rpm": 0,
                "speed_kmh": 0,
                "fuel_pct": 140,
                "ect_c": 80,
                "batt_v": 12.6,
                "odo_km": 0,
            }
        )
        self.assertEqual(data["fuel_pct"], 100.0)

    def test_try_parse_junk(self) -> None:
        self.assertIsNone(try_parse_line("not-json"))
        self.assertIsNone(try_parse_line(""))

    def test_lamps_must_be_object(self) -> None:
        raw = json.dumps(
            {
                "rpm": 0,
                "speed_kmh": 0,
                "fuel_pct": 10,
                "ect_c": 80,
                "batt_v": 12.6,
                "odo_km": 0,
                "lamps": ["oil"],
            }
        )
        with self.assertRaises(ProtocolError):
            parse_line(raw)

    def test_oem_extra_lamps_pass_through(self) -> None:
        raw = json.dumps(
            {
                "rpm": 1200,
                "speed_kmh": 0,
                "fuel_pct": 40,
                "ect_c": 80,
                "batt_v": 12.6,
                "odo_km": 10,
                "lamps": {
                    "brake": True,
                    "door": True,
                    "srs": False,
                    "immobilizer": True,
                    "maint": True,
                    "eps": False,
                    "seatbelt": True,
                },
            }
        )
        parsed = parse_line(raw)
        self.assertTrue(parsed.lamp("brake"))
        self.assertTrue(parsed.lamp("door"))
        self.assertFalse(parsed.lamp("srs"))
        self.assertTrue(parsed.lamp("immobilizer"))
        for key in REQUIRED_FIELDS:
            self.assertIn(key, parsed.to_dict())


if __name__ == "__main__":
    unittest.main()

