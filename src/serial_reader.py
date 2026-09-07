"""Phase 2 stub: optional pyserial reader for Telemetry JSON lines.

Phase 1 is wall-powered bench mock (stdin JSON). This module is wired
via `gauge_ui.py --serial [PORT]` for later UART from an ESP32.

Do not splice the OEM cluster. Overlay path: factory cluster stays
plugged so the legal odometer keeps counting. Phase 2 will add high-Z
taps on a subset of signals — this file does not implement those taps.
"""
from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocol import SERIAL_BAUD, Telemetry, try_parse_line


class SerialUnavailable(RuntimeError):
    """pyserial missing, port missing, or serial layer not ready."""


def _import_serial():
    try:
        import serial  # type: ignore
    except ImportError as e:
        raise SerialUnavailable(
            "pyserial is optional and not installed (Phase 2). "
            "Install with: pip install pyserial"
        ) from e
    return serial


def open_serial(port: str, baud: int = SERIAL_BAUD, timeout: float = 0.05):
    """Open a UART port. Raises SerialUnavailable if pyserial is absent."""
    serial = _import_serial()
    try:
        return serial.Serial(port, baud, timeout=timeout)
    except Exception as e:
        raise SerialUnavailable(f"cannot open {port}: {e}") from e


def iter_serial_lines(
    port: str,
    baud: int = SERIAL_BAUD,
    timeout: float = 0.05,
) -> Iterator[str]:
    """Yield raw newline-delimited strings from UART (Phase 2)."""
    ser = open_serial(port, baud=baud, timeout=timeout)
    try:
        while True:
            raw = ser.readline()
            if not raw:
                continue
            yield raw.decode("utf-8", errors="ignore")
    finally:
        ser.close()


def read_telemetry(port: str, baud: int = SERIAL_BAUD) -> Optional[Telemetry]:
    """Blocking: next valid Telemetry frame, or None on a junk line."""
    for line in iter_serial_lines(port, baud=baud):
        parsed = try_parse_line(line)
        if parsed is not None:
            return parsed
    return None
