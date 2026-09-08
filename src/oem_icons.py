"""AP1 OEM telltales — colours, strip order, and icon artwork.

Telltales follow the AP1 self-test lamp strip (left → right after the
signal pair): ABS, BRAKE, battery, oil, CEL, immobilizer, MAINT REQ'D,
EPS, seatbelt, door, SRS. Turn arrows are green; high beam is ISO blue
(not neon cyan).

Icons are white-on-transparent PNG/SVG under ``assets/icons/`` and tinted
at draw time. Protocol JSON field names are unchanged; extra lamp keys
(``brake``, ``door``, ``srs``, …) pass through as optional booleans.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

# --- OEM telltale colours (back-lit plastic, not UI chrome) -----------------
LAMP_RED = (214, 34, 30)
LAMP_AMBER = (228, 138, 26)
LAMP_GREEN = (44, 196, 88)
LAMP_BLUE = (28, 86, 214)
LAMP_GHOST = (40, 36, 32)

# Reject the old neon sweep / high-beam cyan
NEON_CYAN = (72, 210, 230)

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "icons"

# kind, lamps-dict key, colour, slot width (px at 1920×1080)
# Signal pair first, then the self-test strip order, then right turn.
_LAMP_ROWS: tuple[tuple[str, str, tuple[int, int, int], int], ...] = (
    ("turn_l", "turn_l", LAMP_GREEN, 40),
    ("high_beam", "high_beam", LAMP_BLUE, 44),
    ("abs", "abs", LAMP_AMBER, 50),
    ("brake", "brake", LAMP_RED, 72),
    ("battery", "batt_warn", LAMP_RED, 40),
    ("oil", "oil", LAMP_RED, 42),
    ("cel", "cel", LAMP_AMBER, 50),
    ("immobilizer", "immobilizer", LAMP_GREEN, 40),
    ("maint", "maint", LAMP_AMBER, 54),
    ("eps", "eps", LAMP_AMBER, 42),
    ("seatbelt", "seatbelt", LAMP_RED, 36),
    ("door", "door", LAMP_RED, 46),
    ("srs", "srs", LAMP_RED, 42),
    ("turn_r", "turn_r", LAMP_GREEN, 40),
)

ICON_KINDS: tuple[str, ...] = tuple(row[0] for row in _LAMP_ROWS)


@dataclass(frozen=True)
class LampDef:
    kind: str
    key: str
    color: tuple[int, int, int]
    width: int


@dataclass(frozen=True)
class LampState:
    kind: str
    key: str
    lit: bool
    color: tuple[int, int, int]
    width: int


LAMPS: tuple[LampDef, ...] = tuple(
    LampDef(kind, key, color, width) for kind, key, color, width in _LAMP_ROWS
)


def lamp_strip_inner_width(pad: int = 16) -> int:
    return sum(lamp.width for lamp in LAMPS) + pad


def lamp_color_for(kind: str) -> tuple[int, int, int]:
    for lamp in LAMPS:
        if lamp.kind == kind:
            return lamp.color
    raise KeyError(kind)


def is_neon_cyan(color: Sequence[int]) -> bool:
    """True for the old high-beam / sweep cyan — must not appear on lamps."""
    r, g, b = (int(color[0]), int(color[1]), int(color[2]))
    return b > 180 and g > 180 and r < 120


def lamp_states(
    lamps: dict[str, bool] | None,
    *,
    bulb_check: bool = False,
    batt_low: bool = False,
) -> list[LampState]:
    """Resolve the OEM strip. Extra / unknown keys are ignored here."""
    flags = lamps or {}
    out: list[LampState] = []
    for spec in LAMPS:
        extra = spec.key == "batt_warn" and batt_low
        lit = True if bulb_check else bool(flags.get(spec.key, False) or extra)
        out.append(
            LampState(
                kind=spec.kind,
                key=spec.key,
                lit=lit,
                color=spec.color,
                width=spec.width,
            )
        )
    return out


def _font(pygame, size: int, bold: bool = True):
    return pygame.font.SysFont(
        ["DejaVu Sans", "FreeSans", "sans-serif"], size, bold=bold
    )


def tint_white(pygame, surf, color: tuple[int, int, int]):
    out = surf.copy()
    out.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def blit_glow(pygame, dest, src, center: tuple[int, int], strength: float = 0.5, scale: float = 1.16) -> None:
    """Soft bloom: a larger, faded copy under the sharp sprite."""
    gw = max(2, int(src.get_width() * scale))
    gh = max(2, int(src.get_height() * scale))
    glow = pygame.transform.smoothscale(src, (gw, gh))
    glow.set_alpha(int(255 * max(0.0, min(1.0, strength))))
    dest.blit(glow, glow.get_rect(center=center))
    dest.blit(src, src.get_rect(center=center))


def _blank(pygame, w: int, h: int):
    return pygame.Surface((w, h), pygame.SRCALPHA)


def _draw_text_block(pygame, lines: Iterable[str], w: int, h: int, size: int):
    s = _blank(pygame, w, h)
    font = _font(pygame, size)
    imgs = [font.render(line, True, (255, 255, 255)) for line in lines]
    total_h = sum(img.get_height() for img in imgs) - 2 * max(0, len(imgs) - 1)
    y = (h - total_h) // 2
    for img in imgs:
        s.blit(img, img.get_rect(midtop=(w // 2, y)))
        y += img.get_height() - 2
    return s


def _draw_turn(pygame, w: int, h: int, left: bool):
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2
    if left:
        pts = [(cx + 11, cy - 11), (cx - 13, cy), (cx + 11, cy + 11)]
    else:
        pts = [(cx - 11, cy - 11), (cx + 13, cy), (cx - 11, cy + 11)]
    pygame.draw.polygon(s, (255, 255, 255), pts)
    return s


def _draw_high_beam(pygame, w: int, h: int):
    """ISO 2575 high-beam: D-lamp + parallel rays (blue when lit)."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2 - 4, h // 2
    pygame.draw.circle(s, (255, 255, 255), (cx - 2, cy), 9, 2)
    pygame.draw.arc(s, (255, 255, 255), (cx - 12, cy - 10, 12, 20), 1.2, 5.1, 2)
    for i, dy in enumerate((-8, -3, 3, 8)):
        x0 = cx + 8
        pygame.draw.line(s, (255, 255, 255), (x0, cy + dy), (x0 + 12, cy + dy - 1), 2)
    return s


def _draw_battery(pygame, w: int, h: int):
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2
    pygame.draw.rect(s, (255, 255, 255), (cx - 13, cy - 7, 26, 16), width=2, border_radius=2)
    pygame.draw.rect(s, (255, 255, 255), (cx - 8, cy - 11, 6, 4))
    pygame.draw.rect(s, (255, 255, 255), (cx + 2, cy - 11, 6, 4))
    pygame.draw.line(s, (255, 255, 255), (cx - 6, cy + 1), (cx - 2, cy + 1), 2)
    pygame.draw.line(s, (255, 255, 255), (cx + 3, cy + 1), (cx + 7, cy + 1), 2)
    pygame.draw.line(s, (255, 255, 255), (cx + 5, cy - 1), (cx + 5, cy + 3), 2)
    return s


def _draw_oil(pygame, w: int, h: int):
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2 + 1
    pygame.draw.rect(s, (255, 255, 255), (cx - 11, cy - 5, 18, 11), border_radius=2)
    pygame.draw.polygon(s, (255, 255, 255), [(cx + 6, cy - 5), (cx + 14, cy - 12), (cx + 16, cy - 9), (cx + 8, cy - 2)])
    pygame.draw.circle(s, (255, 255, 255), (cx - 10, cy + 8), 3)
    pygame.draw.ellipse(s, (255, 255, 255), (cx - 12, cy + 9, 5, 6))
    return s


def _draw_cel(pygame, w: int, h: int):
    """Engine block with CHECK — Honda-style CEL, not a generic chip."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2
    pygame.draw.rect(s, (255, 255, 255), (cx - 14, cy - 6, 28, 13), width=2, border_radius=2)
    pygame.draw.rect(s, (255, 255, 255), (cx - 6, cy - 11, 12, 5), width=2)
    pygame.draw.line(s, (255, 255, 255), (cx - 14, cy + 1), (cx - 19, cy + 5), 2)
    pygame.draw.line(s, (255, 255, 255), (cx + 14, cy + 1), (cx + 19, cy + 5), 2)
    font = _font(pygame, 8)
    img = font.render("CHECK", True, (255, 255, 255))
    s.blit(img, img.get_rect(center=(cx, cy + 1)))
    return s


def _draw_key(pygame, w: int, h: int):
    s = _blank(pygame, w, h)
    cx, cy = w // 2 - 2, h // 2
    pygame.draw.circle(s, (255, 255, 255), (cx - 8, cy), 8, 2)
    pygame.draw.circle(s, (255, 255, 255), (cx - 8, cy), 3)
    pygame.draw.rect(s, (255, 255, 255), (cx - 1, cy - 3, 16, 6), border_radius=1)
    pygame.draw.rect(s, (255, 255, 255), (cx + 8, cy - 3, 3, 9))
    pygame.draw.rect(s, (255, 255, 255), (cx + 12, cy - 3, 3, 7))
    return s


def _draw_seatbelt(pygame, w: int, h: int):
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2 + 1
    pygame.draw.circle(s, (255, 255, 255), (cx, cy - 10), 5, 2)
    pygame.draw.arc(s, (255, 255, 255), (cx - 10, cy - 6, 20, 22), 3.5, 6.0, 2)
    pygame.draw.line(s, (255, 255, 255), (cx - 8, cy + 10), (cx + 9, cy - 4), 3)
    return s


def _draw_door(pygame, w: int, h: int):
    """Top-view car with both doors ajar — AP1 door lamp."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2
    pygame.draw.rect(s, (255, 255, 255), (cx - 7, cy - 11, 14, 22), width=2, border_radius=4)
    pygame.draw.rect(s, (255, 255, 255), (cx - 5, cy - 14, 10, 4), width=2, border_radius=2)
    pygame.draw.line(s, (255, 255, 255), (cx - 7, cy - 4), (cx - 15, cy - 8), 2)
    pygame.draw.line(s, (255, 255, 255), (cx - 7, cy + 4), (cx - 15, cy + 1), 2)
    pygame.draw.line(s, (255, 255, 255), (cx + 7, cy - 4), (cx + 15, cy - 8), 2)
    pygame.draw.line(s, (255, 255, 255), (cx + 7, cy + 4), (cx + 15, cy + 1), 2)
    return s


_DRAWERS = {
    "turn_l": lambda pygame, w, h: _draw_turn(pygame, w, h, True),
    "turn_r": lambda pygame, w, h: _draw_turn(pygame, w, h, False),
    "high_beam": _draw_high_beam,
    "battery": _draw_battery,
    "oil": _draw_oil,
    "cel": _draw_cel,
    "immobilizer": _draw_key,
    "seatbelt": _draw_seatbelt,
    "door": _draw_door,
    "abs": lambda pygame, w, h: _draw_text_block(pygame, ("ABS",), w, h, 15),
    "brake": lambda pygame, w, h: _draw_text_block(pygame, ("BRAKE",), w, h, 14),
    "eps": lambda pygame, w, h: _draw_text_block(pygame, ("EPS",), w, h, 15),
    "srs": lambda pygame, w, h: _draw_text_block(pygame, ("SRS",), w, h, 15),
    "maint": lambda pygame, w, h: _draw_text_block(pygame, ("MAINT", "REQ'D"), w, h, 11),
}


def draw_white_icon(pygame, kind: str, w: int = 64, h: int = 48):
    drawer = _DRAWERS.get(kind)
    if drawer is None:
        s = _blank(pygame, w, h)
        pygame.draw.circle(s, (255, 255, 255), (w // 2, h // 2), 6)
        return s
    return drawer(pygame, w, h)


def _load_png(pygame, kind: str):
    path = ASSETS / f"{kind}.png"
    if not path.is_file():
        return None
    img = pygame.image.load(str(path)).convert_alpha()
    return img


def render_icon(pygame, kind: str, color: tuple[int, int, int], height: int):
    png = _load_png(pygame, kind)
    if png is not None:
        scale = height / max(1, png.get_height())
        size = (max(2, int(png.get_width() * scale)), max(2, height))
        white = pygame.transform.smoothscale(png, size)
    else:
        white = draw_white_icon(pygame, kind, w=max(48, int(height * 1.7)), h=height)
        if white.get_height() != height:
            scale = height / max(1, white.get_height())
            white = pygame.transform.smoothscale(
                white,
                (max(2, int(white.get_width() * scale)), height),
            )
    return tint_white(pygame, white, color)


def icon_surface(pygame, kind: str, color: tuple[int, int, int], height: int = 34):
    return render_icon(pygame, kind, color, height)


def export_pngs(pygame, dest: Path | None = None, height: int = 96) -> list[Path]:
    """Write white-on-transparent PNGs for each telltale."""
    dest = dest or ASSETS
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for kind in ICON_KINDS:
        spec = next(lamp for lamp in LAMPS if lamp.kind == kind)
        w = max(96, int(height * spec.width / 34))
        surf = draw_white_icon(pygame, kind, w=w, h=height)
        path = dest / f"{kind}.png"
        pygame.image.save(surf, str(path))
        written.append(path)
    return written


def iter_icon_assets() -> list[Path]:
    return [ASSETS / f"{kind}.svg" for kind in ICON_KINDS] + [
        ASSETS / f"{kind}.png" for kind in ICON_KINDS
    ]
