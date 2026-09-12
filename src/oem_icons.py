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
LAMP_RED = (226, 40, 32)
LAMP_AMBER = (236, 148, 28)
LAMP_GREEN = (40, 204, 92)
LAMP_BLUE = (36, 96, 228)
LAMP_GHOST = (44, 40, 36)

# Reject the old neon sweep / high-beam cyan
NEON_CYAN = (72, 210, 230)

ASSETS = Path(__file__).resolve().parents[1] / "assets" / "icons"

# kind, lamps-dict key, colour, slot width (px at 1920×1080)
# Signal pair first, then the self-test strip order, then right turn.
_LAMP_ROWS: tuple[tuple[str, str, tuple[int, int, int], int], ...] = (
    ("turn_l", "turn_l", LAMP_GREEN, 42),
    ("high_beam", "high_beam", LAMP_BLUE, 46),
    ("abs", "abs", LAMP_AMBER, 52),
    ("brake", "brake", LAMP_RED, 76),
    ("battery", "batt_warn", LAMP_RED, 42),
    ("oil", "oil", LAMP_RED, 44),
    ("cel", "cel", LAMP_AMBER, 54),
    ("immobilizer", "immobilizer", LAMP_GREEN, 42),
    ("maint", "maint", LAMP_AMBER, 56),
    ("eps", "eps", LAMP_AMBER, 44),
    ("seatbelt", "seatbelt", LAMP_RED, 38),
    ("door", "door", LAMP_RED, 46),
    ("srs", "srs", LAMP_RED, 44),
    ("turn_r", "turn_r", LAMP_GREEN, 42),
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


LAMP_GAP = 6


def lamp_strip_inner_width(pad: int = 16) -> int:
    gaps = LAMP_GAP * max(0, len(LAMPS) - 1)
    return sum(lamp.width for lamp in LAMPS) + gaps + pad


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


_FONTS = Path(__file__).resolve().parents[1] / "assets" / "fonts"


def _font(pygame, size: int, bold: bool = True):
    bundled = _FONTS / "BarlowCondensed-Bold.ttf"
    if bundled.is_file():
        try:
            return pygame.font.Font(str(bundled), size)
        except (OSError, pygame.error):
            pass
    return pygame.font.SysFont(
        ["DejaVu Sans", "FreeSans", "sans-serif"], size, bold=bold
    )


def tint_white(pygame, surf, color: tuple[int, int, int]):
    out = surf.copy()
    out.fill((*color, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return out


def blit_glow(pygame, dest, src, center: tuple[int, int], strength: float = 0.62, scale: float = 1.22) -> None:
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
        pts = [
            (cx + 14, cy - 13),
            (cx - 16, cy),
            (cx + 14, cy + 13),
            (cx + 14, cy + 5),
            (cx + 22, cy + 5),
            (cx + 22, cy - 5),
            (cx + 14, cy - 5),
        ]
    else:
        pts = [
            (cx - 14, cy - 13),
            (cx + 16, cy),
            (cx - 14, cy + 13),
            (cx - 14, cy + 5),
            (cx - 22, cy + 5),
            (cx - 22, cy - 5),
            (cx - 14, cy - 5),
        ]
    pygame.draw.polygon(s, (255, 255, 255), pts)
    return s


def _draw_high_beam(pygame, w: int, h: int):
    """ISO 2575 high-beam: hollow D-lamp + three parallel rays."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2 + 7, h // 2
    pygame.draw.circle(s, (255, 255, 255), (cx, cy), 11)
    pygame.draw.rect(s, (255, 255, 255), (cx - 14, cy - 11, 14, 22))
    pygame.draw.circle(s, (0, 0, 0, 0), (cx + 1, cy), 7)
    pygame.draw.rect(s, (0, 0, 0, 0), (cx - 10, cy - 7, 12, 14))
    for i, dy in enumerate((-9, 0, 9)):
        x0 = 4 if i in (0, 2) else 3
        pygame.draw.rect(s, (255, 255, 255), (x0, int(cy + dy - 1.6), cx - 18 - x0, 3))
    return s


def _draw_battery(pygame, w: int, h: int):
    """ISO battery: hollow case, terminals, plus / minus."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2 + 1
    pygame.draw.rect(s, (255, 255, 255), (cx - 18, cy - 8, 36, 22), border_radius=1)
    s.fill((0, 0, 0, 0), pygame.Rect(cx - 14, cy - 4, 28, 14))
    pygame.draw.rect(s, (255, 255, 255), (cx - 11, cy - 13, 8, 5), border_radius=1)
    pygame.draw.rect(s, (255, 255, 255), (cx + 3, cy - 13, 8, 5), border_radius=1)
    pygame.draw.rect(s, (255, 255, 255), (cx - 11, cy + 2, 10, 3))
    pygame.draw.rect(s, (255, 255, 255), (cx - 8, cy - 2, 3, 11))
    pygame.draw.rect(s, (255, 255, 255), (cx + 3, cy + 2, 10, 3))
    return s


def _draw_oil(pygame, w: int, h: int):
    """ISO oil-can: C-handle, hollow body, spout, drop."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2 - 2, h // 2 + 2
    pygame.draw.rect(s, (255, 255, 255), (cx - 24, cy - 8, 10, 18), border_radius=5)
    s.fill((0, 0, 0, 0), pygame.Rect(cx - 21, cy - 4, 7, 10))
    pygame.draw.rect(s, (255, 255, 255), (cx - 16, cy - 9, 26, 20))
    s.fill((0, 0, 0, 0), pygame.Rect(cx - 12, cy - 5, 18, 12))
    pygame.draw.polygon(
        s,
        (255, 255, 255),
        [(cx + 8, cy - 9), (cx + 22, cy - 22), (cx + 28, cy - 15), (cx + 12, cy - 2)],
    )
    s.fill((0, 0, 0, 0), pygame.Rect(cx + 12, cy - 12, 8, 6))
    pygame.draw.polygon(
        s,
        (255, 255, 255),
        [(cx + 24, cy - 12), (cx + 30, cy - 2), (cx + 26, cy + 7), (cx + 21, cy - 2)],
    )
    return s


def _draw_cel(pygame, w: int, h: int):
    """ISO engine block with CHECK punched as negative space."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2
    pygame.draw.rect(s, (255, 255, 255), (cx - 19, cy - 6, 38, 18), border_radius=1)
    pygame.draw.rect(s, (255, 255, 255), (cx - 9, cy - 15, 18, 10), border_radius=1)
    pygame.draw.rect(s, (255, 255, 255), (cx - 26, cy - 2, 8, 10))
    pygame.draw.rect(s, (255, 255, 255), (cx + 18, cy - 2, 8, 10))
    pygame.draw.rect(s, (255, 255, 255), (cx + 25, cy + 2, 6, 12))
    font = _font(pygame, max(8, h // 5))
    check = font.render("CHECK", True, (255, 255, 255))
    box = check.get_rect(center=(cx, cy + 2))
    for y in range(check.get_height()):
        for x in range(check.get_width()):
            if check.get_at((x, y)).a > 80:
                px, py = box.x + x, box.y + y
                if 0 <= px < w and 0 <= py < h:
                    s.set_at((px, py), (0, 0, 0, 0))
    return s


def _draw_key(pygame, w: int, h: int):
    s = _blank(pygame, w, h)
    cx, cy = w // 2 - 2, h // 2
    pygame.draw.circle(s, (255, 255, 255), (cx - 8, cy), 10)
    pygame.draw.circle(s, (0, 0, 0), (cx - 8, cy), 4)
    pygame.draw.rect(s, (255, 255, 255), (cx - 1, cy - 3, 20, 6), border_radius=1)
    pygame.draw.rect(s, (255, 255, 255), (cx + 9, cy + 2, 3, 8))
    pygame.draw.rect(s, (255, 255, 255), (cx + 14, cy + 2, 3, 10))
    return s


def _draw_seatbelt(pygame, w: int, h: int):
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2 + 1
    pygame.draw.circle(s, (255, 255, 255), (cx, cy - 14), 7)
    pygame.draw.circle(s, (0, 0, 0, 0), (cx, cy - 14), 3)
    pygame.draw.polygon(
        s,
        (255, 255, 255),
        [
            (cx - 11, cy - 6),
            (cx + 11, cy - 6),
            (cx + 10, cy + 18),
            (cx - 10, cy + 18),
        ],
    )
    pygame.draw.line(s, (0, 0, 0, 0), (cx - 9, cy - 6), (cx + 10, cy + 17), 7)
    return s


def _draw_door(pygame, w: int, h: int):
    """Top-view car with both doors ajar — AP1 door lamp."""
    s = _blank(pygame, w, h)
    cx, cy = w // 2, h // 2
    pygame.draw.rect(s, (255, 255, 255), (cx - 8, cy - 16, 16, 32), border_radius=5)
    s.fill((0, 0, 0, 0), pygame.Rect(cx - 4, cy - 12, 8, 6))
    pygame.draw.polygon(
        s, (255, 255, 255), [(cx - 8, cy - 2), (cx - 20, cy + 4), (cx - 17, cy + 10), (cx - 8, cy + 4)]
    )
    pygame.draw.polygon(
        s, (255, 255, 255), [(cx + 8, cy - 2), (cx + 20, cy + 4), (cx + 17, cy + 10), (cx + 8, cy + 4)]
    )
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
    "abs": lambda pygame, w, h: _draw_text_block(pygame, ("ABS",), w, h, 18),
    "brake": lambda pygame, w, h: _draw_text_block(pygame, ("BRAKE",), w, h, 17),
    "eps": lambda pygame, w, h: _draw_text_block(pygame, ("EPS",), w, h, 18),
    "srs": lambda pygame, w, h: _draw_text_block(pygame, ("SRS",), w, h, 18),
    "maint": lambda pygame, w, h: _draw_text_block(pygame, ("MAINT", "REQ'D"), w, h, 13),
}


def draw_white_icon(pygame, kind: str, w: int = 64, h: int = 48):
    drawer = _DRAWERS.get(kind)
    if drawer is None:
        s = _blank(pygame, w, h)
        pygame.draw.circle(s, (255, 255, 255), (w // 2, h // 2), 6)
        return s
    return drawer(pygame, w, h)


_TRIM_CACHE: dict[str, object] = {}


def _load_png(pygame, kind: str):
    path = ASSETS / f"{kind}.png"
    if not path.is_file():
        return None
    img = pygame.image.load(str(path)).convert_alpha()
    return img


def _load_trimmed(pygame, kind: str):
    cached = _TRIM_CACHE.get(kind)
    if cached is not None:
        return cached
    png = _load_png(pygame, kind)
    if png is None:
        return None
    trimmed = _trim_alpha(pygame, png)
    _TRIM_CACHE[kind] = trimmed
    return trimmed


def _trim_alpha(pygame, surf, pad: int = 1):
    """Crop transparent padding so slot scale uses the silhouette, not the plate."""
    w, h = surf.get_size()
    min_x, min_y, max_x, max_y = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            if surf.get_at((x, y)).a > 16:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x < min_x:
        return surf
    min_x = max(0, min_x - pad)
    min_y = max(0, min_y - pad)
    max_x = min(w - 1, max_x + pad)
    max_y = min(h - 1, max_y + pad)
    rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
    return surf.subsurface(rect).copy()


def _fit(pygame, surf, max_w: int, max_h: int):
    sw, sh = surf.get_size()
    scale = min(max_w / max(1, sw), max_h / max(1, sh))
    size = (max(2, int(sw * scale)), max(2, int(sh * scale)))
    return pygame.transform.smoothscale(surf, size)


def render_icon(
    pygame,
    kind: str,
    color: tuple[int, int, int],
    height: int,
    max_width: int | None = None,
):
    png = _load_trimmed(pygame, kind)
    if png is not None:
        white = png
    else:
        white = draw_white_icon(pygame, kind, w=max(48, int(height * 1.7)), h=height)
    box_w = max_width or max(height, int(height * 1.7))
    white = _fit(pygame, white, box_w, height)
    return tint_white(pygame, white, color)


def icon_surface(
    pygame,
    kind: str,
    color: tuple[int, int, int],
    height: int = 34,
    max_width: int | None = None,
):
    return render_icon(pygame, kind, color, height, max_width=max_width)


def export_pngs(pygame, dest: Path | None = None, height: int = 96) -> list[Path]:
    """Write white-on-transparent PNGs. Prefer rsvg from SVG plates."""
    dest = dest or ASSETS
    dest.mkdir(parents=True, exist_ok=True)
    try:
        from rasterize_icons import rasterize  # type: ignore

        return [rasterize(kind, height=height) for kind in ICON_KINDS]
    except (FileNotFoundError, OSError, ImportError):
        pass
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
