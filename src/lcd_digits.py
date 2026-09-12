"""OEM-style 7-segment LCD digits with ghost segments and bloom.

Speed / odo windows are red LCD (AP1 photo). Protocol field names are
unchanged — this is display-only.
"""
from __future__ import annotations

from typing import Iterable

# Standard 7-seg names: A top, B UR, C LR, D bot, E LL, F UL, G mid
SEGMENTS = "abcdefg"

DIGIT_SEGS: dict[str, str] = {
    "0": "abcdef",
    "1": "bc",
    "2": "abged",
    "3": "abcdg",
    "4": "bcfg",
    "5": "acdfg",
    "6": "acdefg",
    "7": "abc",
    "8": "abcdefg",
    "9": "abcdfg",
    "-": "g",
    " ": "",
    ".": "",
}


def segs_for(ch: str) -> str:
    return DIGIT_SEGS.get(ch, "")


def ghost_pattern(width: int, fill: str = "8") -> str:
    """Unlit 7-seg silhouette (OEM self-test is 188 / 888888 / 888.8)."""
    return fill * max(0, width)


def _h_seg(x: float, y: float, w: float, t: float) -> list[tuple[float, float]]:
    """Horizontal segment — rounded hex (softer OEM LCD, not square bricks)."""
    notch = t * 0.78
    return [
        (x + notch, y),
        (x + w - notch, y),
        (x + w, y + t * 0.5),
        (x + w - notch, y + t),
        (x + notch, y + t),
        (x, y + t * 0.5),
    ]


def _v_seg(x: float, y: float, h: float, t: float) -> list[tuple[float, float]]:
    """Vertical segment — rounded hex with the same end treatment as `_h_seg`."""
    notch = t * 0.78
    return [
        (x + t * 0.5, y),
        (x + t, y + notch),
        (x + t, y + h - notch),
        (x + t * 0.5, y + h),
        (x, y + h - notch),
        (x, y + notch),
    ]


def segment_polys(x: int, y: int, w: int, h: int) -> dict[str, list[tuple[int, int]]]:
    """Pixel polygons for one digit. Origin is top-left of the digit box."""
    t = max(2.4, h * 0.118)
    t_g = t * 1.08
    gap = max(1.6, t * 0.38)
    inner_w = w - t
    half = (h - t) / 2.0
    ax, ay = x + t * 0.35, y
    a = _h_seg(ax, ay, inner_w, t)
    g = _h_seg(ax - t * 0.04, y + half - (t_g - t) * 0.5, inner_w + t * 0.08, t_g)
    d = _h_seg(ax, y + h - t, inner_w, t)
    f = _v_seg(x, y + t * 0.55, half - gap, t)
    b = _v_seg(x + w - t, y + t * 0.55, half - gap, t)
    e = _v_seg(x, y + half + t * 0.35, half - gap, t)
    c = _v_seg(x + w - t, y + half + t * 0.35, half - gap, t)
    out: dict[str, list[tuple[int, int]]] = {}
    for name, pts in (("a", a), ("b", b), ("c", c), ("d", d), ("e", e), ("f", f), ("g", g)):
        out[name] = [(int(round(px)), int(round(py))) for px, py in pts]
    return out


def _expand(pts: list[tuple[int, int]], px: float) -> list[tuple[int, int]]:
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    out: list[tuple[int, int]] = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        n = (dx * dx + dy * dy) ** 0.5 or 1.0
        out.append((int(x + dx / n * px), int(y + dy / n * px)))
    return out


def draw_digit(
    pygame,
    dest,
    ch: str,
    box: tuple[int, int, int, int],
    color: tuple[int, int, int],
    ghost: tuple[int, int, int] | None,
    bloom=None,
) -> None:
    x, y, w, h = box
    polys = segment_polys(x, y, w, h)
    lit = set(segs_for(ch))
    if ghost is not None:
        for pts in polys.values():
            pygame.draw.polygon(dest, ghost, pts)
    for name, pts in polys.items():
        if name not in lit:
            continue
        if bloom is not None:
            glow = (
                min(255, color[0] + 32),
                min(255, color[1] + 18),
                min(255, color[2] + 8),
                102,
            )
            pygame.draw.polygon(bloom, glow, _expand(pts, 6))
        pygame.draw.polygon(dest, color, pts)
        cap_r = max(1, int(round(h * 0.04)))
        pygame.draw.circle(dest, color, pts[0], cap_r)
        pygame.draw.circle(dest, color, pts[len(pts) // 2], cap_r)


def measure_text(text: str, digit_h: int, gap: int | None = None) -> tuple[int, int]:
    """Width × height of a digit string including a decimal point gutter."""
    dw = max(8, int(digit_h * 0.62))
    gap = dw // 6 if gap is None else gap
    width = 0
    for ch in text:
        if ch == ".":
            width += max(4, dw // 5)
        else:
            width += dw + gap
    if text:
        width -= gap
    return width, digit_h


def blit_digits(
    pygame,
    dest,
    text: str,
    center: tuple[int, int],
    digit_h: int,
    color: tuple[int, int, int],
    ghost: tuple[int, int, int] | None = None,
    ghost_text: str | None = None,
    bloom: bool = True,
    italic: float = 0.08,
) -> tuple[int, int, int, int]:
    """Draw ``text`` (digits / space / minus / one '.') centred on ``center``.

    Returns the bounding rect (x, y, w, h). ``ghost_text`` defaults to eights
    so unused digits keep the OEM 188 / 888888 silhouette.
    """
    dw = max(8, int(digit_h * 0.62))
    gap = max(2, dw // 6)
    total_w, _ = measure_text(text, digit_h, gap)
    cx, cy = center
    x0 = cx - total_w // 2
    y0 = cy - digit_h // 2
    bloom_surf = None
    if bloom:
        bloom_surf = pygame.Surface(dest.get_size(), pygame.SRCALPHA)

    gtext = ghost_text if ghost_text is not None else "".join(
        "8" if ch != "." else "." for ch in text
    )
    # Pad ghost to the same length
    if len(gtext) < len(text):
        gtext = gtext.ljust(len(text))
    elif len(gtext) > len(text):
        gtext = gtext[: len(text)]

    x = x0
    for i, ch in enumerate(text):
        shear = int((0.5 * digit_h) * italic)
        if ch == ".":
            r = max(2, digit_h // 14)
            px = x + r
            py = y0 + digit_h - r - 1
            if ghost is not None:
                pygame.draw.circle(dest, ghost, (px, py), r)
            pygame.draw.circle(dest, color, (px, py), r)
            x += max(4, dw // 5)
            continue
        box = (x + shear, y0, dw, digit_h)
        if ghost is not None:
            draw_digit(pygame, dest, gtext[i], box, ghost, ghost=None, bloom=None)
        draw_digit(pygame, dest, ch, box, color, ghost=None, bloom=bloom_surf)
        x += dw + gap

    if bloom_surf is not None:
        small = pygame.transform.smoothscale(
            bloom_surf, (dest.get_width() // 3, dest.get_height() // 3)
        )
        dest.blit(pygame.transform.smoothscale(small, dest.get_size()), (0, 0))

    return (x0, y0, total_w, digit_h)


def lcd_window(
    pygame,
    dest,
    rect: tuple[int, int, int, int],
    wash,
    edge,
    door: tuple[int, int, int, int] = (255, 48, 32, 12),
) -> None:
    """Recessed rectangular LCD well with a light screen-door wash."""
    x, y, w, h = rect
    pygame.draw.rect(dest, wash, pygame.Rect(x, y, w, h), border_radius=3)
    pygame.draw.rect(dest, (28, 10, 8), pygame.Rect(x + 1, y + 1, max(2, w - 2), max(2, h - 2)), width=1, border_radius=2)
    pygame.draw.rect(dest, edge, pygame.Rect(x, y, w, h), width=1, border_radius=3)
    polariser = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(0, w, 3):
        pygame.draw.line(polariser, door, (i, 0), (i, h))
    dest.blit(polariser, (x, y))


def iter_lit_cells(text: str) -> Iterable[str]:
    for ch in text:
        yield segs_for(ch)
