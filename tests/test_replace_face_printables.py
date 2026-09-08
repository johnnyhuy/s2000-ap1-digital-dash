"""Sanity checks for cleaned replace-face printables (no pygame)."""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
