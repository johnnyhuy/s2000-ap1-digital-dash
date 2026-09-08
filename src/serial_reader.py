"""Phase 2 stub: optional pyserial reader for Telemetry JSON lines.

Phase 1 is wall-powered bench mock (stdin JSON). This module is wired
via `gauge_ui.py --serial [PORT]` for later UART from an ESP32.

Do not splice the OEM cluster. Overlay path: factory cluster stays
plugged so the legal odometer keeps counting. Phase 2 will add high-Z
taps on a subset of signals — this file does not implement those taps.

``SerialLineReader`` is the thin consumer used by the UI and by mocked
UART tests (in-memory ``FakeSerial`` or a local PTY). It does not care
whether the bytes came from a real ESP32.
"""
from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Optional, Protocol

sys.path.insert(0, str(Path(__file__).resolve().parent))
from protocol import SERIAL_BAUD, Telemetry, try_parse_line


class SerialUnavailable(RuntimeError):
    """pyserial missing, port missing, or serial layer not ready."""


class SerialLike(Protocol):
    """Minimum surface shared by pyserial and ``mocks.fake_serial.FakeSerial``."""

    @property
    def in_waiting(self) -> int: ...

    def read(self, size: int = 1) -> bytes: ...

    def readline(self) -> bytes: ...

    def close(self) -> None: ...


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


def _decode_chunk(raw: bytes | str) -> str:
    if isinstance(raw, str):
        return raw
    return raw.decode("utf-8", errors="ignore")


class SerialLineReader:
    """Non-blocking newline-JSON consumer for any serial-like object."""

    def __init__(self, ser: SerialLike) -> None:
        self._ser = ser
        self._buf = ""

    def poll(self) -> Optional[Telemetry]:
        """Read whatever is waiting; return the latest valid frame, if any."""
        latest: Optional[Telemetry] = None
        waiting = getattr(self._ser, "in_waiting", 0) or 0
        if waiting:
            self._buf += _decode_chunk(self._ser.read(waiting))
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            parsed = try_parse_line(line)
            if parsed is not None:
                latest = parsed
        return latest


def read_telemetry_from(ser: SerialLike, max_polls: int = 64) -> Optional[Telemetry]:
    """Drain a serial-like object until one valid Telemetry frame appears."""
    reader = SerialLineReader(ser)
    for _ in range(max_polls):
        got = reader.poll()
        if got is not None:
            return got
    return None


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
            yield _decode_chunk(raw)
    finally:
        ser.close()


def read_telemetry(port: str, baud: int = SERIAL_BAUD) -> Optional[Telemetry]:
    """Blocking: next valid Telemetry frame, or None on a junk line."""
    for line in iter_serial_lines(port, baud=baud):
        parsed = try_parse_line(line)
        if parsed is not None:
            return parsed
    return None
