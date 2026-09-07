"""S2000 AP1 Phase 1 — shared JSON telemetry schema.

Wire format: one JSON object per newline (UTF-8).
Required fields match exactly: rpm, speed_kmh, fuel_pct, ect_c, batt_v, odo_km.
Optional: lamps — dict of boolean indicator flags.

Phase 1 emits this from mock_telemetry (bench / wall power).
Phase 2 will emit the same objects over UART after high-Z taps.
The OEM cluster stays plugged (overlay path) so the legal odometer
keeps counting on the factory ECU/cluster, not this display.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

# --- constants ---------------------------------------------------------------

PROTOCOL_VERSION = 1
SERIAL_BAUD = 115200  # Phase 2 UART (ESP32 → Pi)
MOCK_HZ = 20

REQUIRED_FIELDS = (
    "rpm",
    "speed_kmh",
    "fuel_pct",
    "ect_c",
    "batt_v",
    "odo_km",
)

# Known lamp keys (others allowed; unknown keys pass through as bool)
LAMP_KEYS = (
    "oil",
    "cel",
    "abs",
    "turn_l",
    "turn_r",
    "high_beam",
    "fog",
    "fuel_low",
    "batt_warn",
    "ect_hot",
)

RPM_REDLINE = 9000
RPM_VTEC = 6000
SPEED_MAX_KMH = 280
FUEL_LOW_PCT = 15.0
ECT_HOT_C = 105.0
BATT_LOW_V = 12.2


class ProtocolError(ValueError):
    """Invalid telemetry payload."""


@dataclass
class Telemetry:
    rpm: int = 0
    speed_kmh: float = 0.0
    fuel_pct: float = 50.0
    ect_c: float = 85.0
    batt_v: float = 12.6
    odo_km: float = 0.0
    lamps: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Telemetry:
        """Build from a raw mapping after validate()."""
        return cls(**validate(data))

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "rpm": int(self.rpm),
            "speed_kmh": float(self.speed_kmh),
            "fuel_pct": float(self.fuel_pct),
            "ect_c": float(self.ect_c),
            "batt_v": float(self.batt_v),
            "odo_km": float(self.odo_km),
        }
        if self.lamps:
            d["lamps"] = {str(k): bool(v) for k, v in self.lamps.items()}
        return d

    def to_line(self) -> str:
        """Serialize as a single newline-terminated JSON object (no spaces)."""
        return json.dumps(self.to_dict(), separators=(",", ":")) + "\n"

    def lamp(self, key: str, default: bool = False) -> bool:
        return bool(self.lamps.get(key, default))


def validate(data: Mapping[str, Any]) -> dict[str, Any]:
    """Validate a parsed mapping; raise ProtocolError on failure.

    Returns a normalized dict suitable for Telemetry construction.
    Out-of-range fuel is clamped; other numerics are accepted as-is so the
    UI can show a warning rather than dropping the frame.
    """
    if not isinstance(data, Mapping):
        raise ProtocolError("payload must be a JSON object")

    missing = [k for k in REQUIRED_FIELDS if k not in data]
    if missing:
        raise ProtocolError(f"missing required fields: {', '.join(missing)}")

    try:
        rpm = int(data["rpm"])
        speed_kmh = float(data["speed_kmh"])
        fuel_pct = float(data["fuel_pct"])
        ect_c = float(data["ect_c"])
        batt_v = float(data["batt_v"])
        odo_km = float(data["odo_km"])
    except (TypeError, ValueError) as e:
        raise ProtocolError(f"bad numeric field: {e}") from e

    # Soft clamps (display-friendly; do not reject out-of-range)
    if fuel_pct < 0 or fuel_pct > 100:
        fuel_pct = max(0.0, min(100.0, fuel_pct))

    lamps: dict[str, bool] = {}
    raw_lamps = data.get("lamps")
    if raw_lamps is not None:
        if not isinstance(raw_lamps, Mapping):
            raise ProtocolError("lamps must be an object of booleans")
        for k, v in raw_lamps.items():
            lamps[str(k)] = bool(v)

    return {
        "rpm": rpm,
        "speed_kmh": speed_kmh,
        "fuel_pct": fuel_pct,
        "ect_c": ect_c,
        "batt_v": batt_v,
        "odo_km": odo_km,
        "lamps": lamps,
    }


def parse_line(line: str) -> Telemetry:
    """Parse one newline-delimited JSON telemetry object."""
    text = line.strip()
    if not text:
        raise ProtocolError("empty line")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ProtocolError(f"invalid JSON: {e}") from e
    return Telemetry.from_dict(data)


def try_parse_line(line: str) -> Optional[Telemetry]:
    """Parse or return None (never raises)."""
    try:
        return parse_line(line)
    except ProtocolError:
        return None
