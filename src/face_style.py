"""Cluster face style — layout only; protocol fields stay frozen.

AP1 (default): locked flat elevation — straight TEMP / FUEL, OEM telltale strip.
AP2: interpretive arched side-gauges (TEMP over FUEL on the right) plus a
clock row. Geometry is *not* a pixel-perfect AP2 plate — see refs/oem/ap2/.

Future chassis can add more members without renaming JSON fields.
"""
from __future__ import annotations

from enum import Enum


class FaceStyle(str, Enum):
    AP1 = "ap1"
    AP2 = "ap2"


DEFAULT_FACE_STYLE = FaceStyle.AP1

FACE_STYLE_LABELS: dict[FaceStyle, str] = {
    FaceStyle.AP1: "AP1 — straight TEMP / FUEL",
    FaceStyle.AP2: "AP2 — arched side gauges",
}


class FaceStyleError(ValueError):
    """Unknown or empty face style."""


def parse_face_style(value: str | FaceStyle | None) -> FaceStyle:
    """Parse a style token. Blank / None → AP1 default."""
    if value is None or value is FaceStyle.AP1:
        return FaceStyle.AP1
    if isinstance(value, FaceStyle):
        return value
    token = str(value).strip().lower()
    if not token:
        return FaceStyle.AP1
    try:
        return FaceStyle(token)
    except ValueError as exc:
        known = ", ".join(s.value for s in FaceStyle)
        raise FaceStyleError(f"unknown face style {value!r}; expected {known}") from exc
