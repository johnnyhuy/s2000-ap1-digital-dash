"""Serial-like stand-ins for the Phase 2 UART path (no hardware).

``FakeSerial`` matches the small pyserial surface ``SerialLineReader`` uses:
``read``, ``write``, ``readline``, ``in_waiting``, ``close``.
"""
from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Optional


class FakeSerial:
    """In-memory UART. Writes append; reads consume from the same buffer."""

    def __init__(self, initial: bytes | str | Iterable[str] | None = None) -> None:
        self._buf = bytearray()
        self.closed = False
        if initial is None:
            return
        if isinstance(initial, (bytes, bytearray)):
            self._buf.extend(initial)
        elif isinstance(initial, str):
            self.write(initial)
        else:
            for line in initial:
                self.feed_line(line)

    def feed_line(self, line: str) -> None:
        text = line if line.endswith("\n") else f"{line}\n"
        self.write(text)

    @property
    def in_waiting(self) -> int:
        return 0 if self.closed else len(self._buf)

    def write(self, data: bytes | str) -> int:
        if self.closed:
            raise ValueError("write to closed FakeSerial")
        raw = data.encode("utf-8") if isinstance(data, str) else bytes(data)
        self._buf.extend(raw)
        return len(raw)

    def read(self, size: int = 1) -> bytes:
        if self.closed:
            return b""
        n = max(0, int(size))
        chunk = bytes(self._buf[:n])
        del self._buf[:n]
        return chunk

    def readline(self) -> bytes:
        if self.closed:
            return b""
        idx = self._buf.find(b"\n")
        if idx < 0:
            chunk = bytes(self._buf)
            self._buf.clear()
            return chunk
        chunk = bytes(self._buf[: idx + 1])
        del self._buf[: idx + 1]
        return chunk

    def close(self) -> None:
        self.closed = True

    def flush(self) -> None:
        return None


def open_pty_pair() -> tuple[str, int, int]:
    """Return ``(slave_path, master_fd, slave_fd)`` for a local UART loopback."""
    import pty

    master_fd, slave_fd = pty.openpty()
    return os.ttyname(slave_fd), master_fd, slave_fd


def write_pty(master_fd: int, text: str) -> None:
    raw = text.encode("utf-8") if isinstance(text, str) else text
    os.write(master_fd, raw)


def close_pty(master_fd: int, slave_fd: Optional[int] = None) -> None:
    os.close(master_fd)
    if slave_fd is not None:
        os.close(slave_fd)
