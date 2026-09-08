"""7-segment LCD helpers — maps, measure, headless blit."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from lcd_digits import (  # noqa: E402
    DIGIT_SEGS,
    blit_digits,
    ghost_pattern,
    measure_text,
    segs_for,
    segment_polys,
)


class MapTests(unittest.TestCase):
    def test_0_to_9_are_standard_seven_seg(self) -> None:
        self.assertEqual(segs_for("0"), "abcdef")
        self.assertEqual(segs_for("1"), "bc")
        self.assertEqual(segs_for("8"), "abcdefg")
        self.assertEqual(set(segs_for("8")), set("abcdefg"))

    def test_ghost_pattern_eights(self) -> None:
        self.assertEqual(ghost_pattern(3), "888")
        self.assertEqual(ghost_pattern(6), "888888")

    def test_unknown_is_blank(self) -> None:
        self.assertEqual(segs_for("x"), "")

    def test_every_digit_has_only_named_segs(self) -> None:
        for ch, segs in DIGIT_SEGS.items():
            self.assertTrue(set(segs) <= set("abcdefg"), ch)


class GeometryTests(unittest.TestCase):
    def test_seven_polygons(self) -> None:
        polys = segment_polys(0, 0, 40, 70)
        self.assertEqual(set(polys), set("abcdefg"))
        for pts in polys.values():
            self.assertGreaterEqual(len(pts), 4)

    def test_measure_grows_with_digits(self) -> None:
        w3, h3 = measure_text("188", 40)
        w6, h6 = measure_text("888888", 40)
        self.assertEqual(h3, h6)
        self.assertGreater(w6, w3)


class HeadlessBlitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        import pygame

        pygame.init()
        cls.pygame = pygame
        cls.surf = pygame.Surface((400, 200))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pygame.quit()

    def test_blit_188_paints_amber(self) -> None:
        self.surf.fill((0, 0, 0))
        box = blit_digits(
            self.pygame,
            self.surf,
            "188",
            (200, 100),
            digit_h=64,
            color=(236, 152, 32),
            ghost=(40, 26, 10),
            ghost_text="188",
            bloom=False,
        )
        self.assertGreater(box[2], 80)
        amber = 0
        for y in range(0, 200, 4):
            for x in range(0, 400, 4):
                px = self.surf.get_at((x, y))
                if px.r > 180 and px.g > 100 and px.b < 80:
                    amber += 1
        self.assertGreater(amber, 10)


if __name__ == "__main__":
    unittest.main()
