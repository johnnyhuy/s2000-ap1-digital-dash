"""Sanity checks for cleaned replace-face printables (no pygame)."""

from __future__ import annotations

import re
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPLACE = ROOT / "cad" / "replace_face"
PRINT_STL = REPLACE / "print" / "stl"
PRINT_STEP = REPLACE / "print" / "step"
PRINT_OBJ = REPLACE / "print" / "obj"
PREVIEW = REPLACE / "preview" / "assembly.glb"
SCRIPT = REPLACE / "blender_remesh.py"

PARTS = (
    "backlight",
    "backlight_web",
    "acrylic_face",
    "button_rocker",
    "button_sel",
    "button_trip",
)

DIMS_SCAD = REPLACE / "dims.scad"
OUTLINE_SCAD = REPLACE / "outline.scad"
README = REPLACE / "README.md"
BLENDER_MD = REPLACE / "BLENDER.md"

# AP1 lock (#12 / refs/flat/DIMENSIONS.md) — horizontal flanking bars.
LOCK = {
    "face_w": 170.0,
    "face_h": 72.3,
    "face_aspect": 2.35,
    "notch_top_pct": 0.58,
    "notch_bot_pct": 0.72,
    "arch_rise_pct": 0.28,
    "temp_x_pct": 0.080,
    "temp_y_pct": 0.505,
    "fuel_x_pct": 0.760,
    "fuel_y_pct": 0.505,
    "bar_w_pct": 0.160,
    "bar_h_pct": 0.012,
    "temp_segs": 6,
    "speed_x_pct": 0.50,
    "speed_y_pct": 0.40,
}

# Expected bbox after a light clean — must stay on the OpenSCAD lock.
# (min), (max), tolerance mm
BBOX = {
    "acrylic_face": ((0.0, 0.0, 0.0), (170.0, 72.3, 2.0), 0.05),
    "backlight": ((-2.0, -2.0, 0.0), (172.0, 74.3, 12.0), 0.08),
    "backlight_web": ((0.45, 0.45, 0.0), (169.55, 71.85, 3.8), 0.08),
    "button_rocker": ((-1.6, -1.6, 0.0), (17.24, 7.68, 3.6), 0.08),
    "button_sel": ((-0.4, -0.4, 0.0), (10.94, 6.48, 3.6), 0.08),
    "button_trip": ((-0.4, -0.4, 0.0), (10.94, 6.48, 3.6), 0.08),
}


def _read_binary_stl(path: Path):
    data = path.read_bytes()
    if len(data) < 84:
        raise ValueError("too small")
    count = struct.unpack_from("<I", data, 80)[0]
    if 84 + count * 50 != len(data):
        raise ValueError("not a binary STL")
    mn = [1e9, 1e9, 1e9]
    mx = [-1e9, -1e9, -1e9]
    for i in range(count):
        off = 84 + i * 50
        vals = struct.unpack_from("<12f", data, off)
        for v in (vals[3:6], vals[6:9], vals[9:12]):
            for a in range(3):
                mn[a] = min(mn[a], v[a])
                mx[a] = max(mx[a], v[a])
    return count, tuple(mn), tuple(mx)


def _parse_scad_assigns(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8")
    vals: dict[str, float] = {}
    for match in re.finditer(
        r"^([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*;",
        text,
        flags=re.MULTILINE,
    ):
        vals[match.group(1)] = float(match.group(2))
    return vals


class ReplaceFacePrintablesTest(unittest.TestCase):
    def test_blender_script_help_without_bpy(self):
        import subprocess
        import sys

        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("blender --background --python", proc.stdout)

    def test_cleaned_stls_exist_and_keep_lock_bbox(self):
        for part in PARTS:
            path = PRINT_STL / f"{part}.stl"
            self.assertTrue(path.is_file(), f"missing {path}")
            count, mn, mx = _read_binary_stl(path)
            self.assertGreater(count, 10, part)
            exp_min, exp_max, tol = BBOX[part]
            for i, axis in enumerate("xyz"):
                self.assertAlmostEqual(
                    mn[i], exp_min[i], delta=tol, msg=f"{part} min {axis}"
                )
                self.assertAlmostEqual(
                    mx[i], exp_max[i], delta=tol, msg=f"{part} max {axis}"
                )

    def test_faceted_step_and_obj_fallback(self):
        for part in PARTS:
            step = PRINT_STEP / f"{part}.step"
            obj = PRINT_OBJ / f"{part}.obj"
            self.assertTrue(step.is_file(), step)
            text = step.read_text(encoding="ascii", errors="replace")
            self.assertTrue(text.startswith("ISO-10303-21;"), part)
            self.assertIn("END-ISO-10303-21;", text)
            self.assertIn("SI_UNIT(.MILLI.,.METRE.)", text)
            self.assertIn("PLACEHOLDER", text)
            self.assertTrue(obj.is_file(), obj)
            self.assertIn("v ", obj.read_text(encoding="ascii", errors="replace")[:4000])

    def test_assembly_glb_is_binary_gltf(self):
        self.assertTrue(PREVIEW.is_file(), PREVIEW)
        data = PREVIEW.read_bytes()
        self.assertGreater(len(data), 200)
        self.assertEqual(data[:4], b"glTF")

    def test_dims_match_horizontal_flanking_lock(self):
        dims = _parse_scad_assigns(DIMS_SCAD)
        for name, expected in LOCK.items():
            self.assertIn(name, dims, name)
            self.assertAlmostEqual(dims[name], expected, places=3, msg=name)

        # Horizontal envelopes flank the speedo — not a bottom bar, not vertical.
        self.assertGreater(dims["bar_w_pct"], dims["bar_h_pct"] * 6)
        self.assertLess(dims["temp_x_pct"] + dims["bar_w_pct"], dims["speed_x_pct"])
        self.assertGreater(dims["fuel_x_pct"], dims["speed_x_pct"])
        self.assertEqual(dims["temp_y_pct"], dims["fuel_y_pct"])
        self.assertAlmostEqual(dims["face_w"] / dims["face_h"], dims["face_aspect"], places=2)

        text = DIMS_SCAD.read_text(encoding="utf-8")
        self.assertNotRegex(text, r"temp_x_pct\s*=\s*0\.075")
        self.assertNotRegex(text, r"temp_y_pct\s*=\s*0\.72")
        self.assertNotRegex(text, r"bar_w_pct\s*=\s*0\.180")
        self.assertNotRegex(text, r"bar_h_pct\s*=\s*0\.030")

    def test_outline_keeps_horizontal_bar_windows(self):
        text = OUTLINE_SCAD.read_text(encoding="utf-8")
        self.assertIn("module temp_bar_2d()", text)
        self.assertIn("module fuel_bar_2d()", text)
        self.assertIn("temp_w, temp_h", text)
        self.assertIn("fuel_w, fuel_h", text)
        self.assertNotIn("temp_h, temp_w", text)
        self.assertNotIn("fuel_h, fuel_w", text)
        self.assertIn("never a vertical stack", text.lower())

    def test_docs_cite_horizontal_lock_and_dimensions(self):
        readme = README.read_text(encoding="utf-8")
        blender = BLENDER_MD.read_text(encoding="utf-8")
        for text in (readme, blender):
            self.assertIn("DIMENSIONS.md", text)
            self.assertIn("8.0%", text)
            self.assertIn("76.0%", text)
            self.assertIn("50.5%", text)
            self.assertIn("horizontal", text.lower())
            self.assertIn("#12", text)


if __name__ == "__main__":
    unittest.main()
