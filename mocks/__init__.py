"""Isolated bench mocks — no Pi display, no ESP32, no car wiring.

Import ``mocks.esp32_uart`` or ``mocks.fake_serial`` directly so
``python -m mocks.esp32_uart`` does not double-load the emitter.
"""
from __future__ import annotations

__all__ = [
    "OEM_EXTRA_LAMPS",
    "FakeSerial",
    "emit_frames",
    "frame_at",
]


def __getattr__(name: str):
    if name in {"OEM_EXTRA_LAMPS", "emit_frames", "frame_at"}:
        from mocks import esp32_uart

        return getattr(esp32_uart, name)
    if name == "FakeSerial":
        from mocks.fake_serial import FakeSerial

        return FakeSerial
    raise AttributeError(name)
