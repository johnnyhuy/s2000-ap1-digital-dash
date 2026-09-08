"""UI harness — smoke frames, ahash stability, OEM refs present."""
from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts"))
sys.path.insert(0, str(_ROOT / "tests"))

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from ui_harness import (  # noqa: E402
    AHASH_TOLERANCE,
    GOLDEN,
    HARNESS_DIR,
    SCENES,
    ahash,
    check_hashes,
    hamming,
    load_goldens,
    render_scenes,
)


class HashTests(unittest.TestCase):
    def test_identical_hashes_are_zero(self) -> None:
        self.assertEqual(hamming("00ff", "00ff"), 0)

    def test_one_bit_flip(self) -> None:
        self.assertEqual(hamming("0000", "0001"), 1)


class HarnessSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from gauge_ui import build_fonts, init_pygame

        cls.pygame, _screen = init_pygame(windowed=True, headless=True)
        cls.fonts = build_fonts(cls.pygame)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.pygame.quit()

    def test_scenes_write_pngs_and_stable_ahash(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            hashes = render_scenes(self.pygame, self.fonts, dest)
            self.assertEqual(set(hashes), {name for name, *_ in SCENES})
            for name in hashes:
                self.assertTrue((dest / f"{name}.png").is_file())
            again = render_scenes(self.pygame, self.fonts, dest)
            for name, digest in hashes.items():
                self.assertLessEqual(
                    hamming(digest, again[name]),
                    4,
                    f"{name} should rehash identically on the same host",
                )

    def test_ahash_of_blank_vs_pattern_differs(self) -> None:
        blank = self.pygame.Surface((64, 64))
        blank.fill((0, 0, 0))
        patterned = self.pygame.Surface((64, 64))
        patterned.fill((0, 0, 0))
        self.pygame.draw.rect(patterned, (236, 152, 32), (8, 8, 40, 20))
        self.assertNotEqual(ahash(self.pygame, blank), ahash(self.pygame, patterned))

    def test_goldens_match_when_present(self) -> None:
        if not GOLDEN.is_file():
            self.skipTest("goldens.json not committed yet")
        hashes = render_scenes(self.pygame, self.fonts, HARNESS_DIR)
        errors = check_hashes(hashes, load_goldens())
        self.assertEqual(errors, [], "\n".join(errors))


class RefAssetTests(unittest.TestCase):
    def test_sources_markdown_exists(self) -> None:
        src = _ROOT / "refs" / "oem" / "SOURCES.md"
        self.assertTrue(src.is_file())
        text = src.read_text(encoding="utf-8")
        self.assertIn("CC BY", text)
        self.assertIn("AP2", text)

    def test_ap1_lit_photo_committed(self) -> None:
        path = _ROOT / "refs" / "oem" / "lit" / "lit_ap1_carspy_cluster.jpg"
        self.assertTrue(path.is_file())
        self.assertGreater(path.stat().st_size, 20_000)

    def test_ap2_is_clearly_labeled(self) -> None:
        path = _ROOT / "refs" / "oem" / "ap2" / "ap2_s2ki_arched_gauges.jpg"
        self.assertTrue(path.is_file())


if __name__ == "__main__":
    unittest.main()
