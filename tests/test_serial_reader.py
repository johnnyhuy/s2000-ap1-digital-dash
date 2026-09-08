"""Thin serial reader against FakeSerial / in-memory UART."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))

from mocks.esp32_uart import iter_frames, warn_frame  # noqa: E402
from mocks.fake_serial import FakeSerial  # noqa: E402
from protocol import REQUIRED_FIELDS, parse_line  # noqa: E402
from serial_reader import SerialLineReader, read_telemetry_from  # noqa: E402


class SerialReaderTests(unittest.TestCase):
    def test_reader_keeps_latest_valid_frame(self) -> None:
        first, second = list(iter_frames(2, scenario="drive"))
        ser = FakeSerial()
        ser.feed_line("junk")
        ser.feed_line(first.to_line())
        ser.feed_line(second.to_line())
        got = SerialLineReader(ser).poll()
        self.assertIsNotNone(got)
        self.assertEqual(got.rpm, second.rpm)
        self.assertEqual(got.odo_km, second.odo_km)
        for key in REQUIRED_FIELDS:
            self.assertIn(key, got.to_dict())

    def test_partial_line_waits_for_newline(self) -> None:
        telem = warn_frame()
        raw = telem.to_line()
        ser = FakeSerial(raw[:20])
        reader = SerialLineReader(ser)
        self.assertIsNone(reader.poll())
        ser.write(raw[20:])
        got = reader.poll()
        self.assertIsNotNone(got)
        self.assertEqual(got.rpm, telem.rpm)
        self.assertTrue(got.lamp("brake"))

    def test_read_telemetry_from_skips_junk(self) -> None:
        telem = warn_frame()
        ser = FakeSerial(["{nope}\n", telem.to_line()])
        got = read_telemetry_from(ser)
        self.assertIsNotNone(got)
        parsed = parse_line(telem.to_line())
        self.assertEqual(got.rpm, parsed.rpm)
        self.assertAlmostEqual(got.batt_v, parsed.batt_v)

    def test_closed_serial_yields_nothing(self) -> None:
        ser = FakeSerial([warn_frame().to_line()])
        ser.close()
        self.assertIsNone(read_telemetry_from(ser, max_polls=3))


if __name__ == "__main__":
    unittest.main()
