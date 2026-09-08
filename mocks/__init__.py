"""Isolated bench mocks — no Pi display, no ESP32, no car wiring.

``esp32_uart`` speaks the frozen Phase 2 newline JSON at ~20 Hz.
``fake_serial`` is an in-memory / pty stand-in for pyserial.
"""
from __future__ import annotations

from mocks.esp32_uart import OEM_EXTRA_LAMPS, emit_frames, frame_at
from mocks.fake_serial import FakeSerial

__all__ = [
    "OEM_EXTRA_LAMPS",
    "FakeSerial",
    "emit_frames",
    "frame_at",
]
