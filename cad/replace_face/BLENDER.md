# Blender remesh — replace-face printables

**Not a verified AP1 drop-in.** Callipers are still `PLACEHOLDER`. OpenSCAD
(`dims.scad`, `outline.scad`, `parts.scad`) is the parametric source of
truth — this pass only cleans the one-body CGAL dumps. Do not invent
stems, clips, pin bosses, or Honda connector pitch here.

Face lock follows [`refs/flat/DIMENSIONS.md`](../../refs/flat/DIMENSIONS.md)
and PR [#12](https://github.com/johnnyhuy/s2000-digital-dash/pull/12):
**horizontal TEMP** at **(8.0%, 50.5%)** left of the speedo, **FUEL** at
**(76.0%, 50.5%)** right (w = 16%, h = 1.2%). Vertical TEMP/FUEL stacks
are erroneous. Silhouette stays 170 × 72.3, 2.35:1, flat bottom,
rectangular 58–72% notches, parabola `y% = 28 u²`.

## Run

Headless (CI-friendly if Blender is on `PATH`):

```bash
blender --background --python cad/replace_face/blender_remesh.py
```

Or `python3 cad/replace_face/blender_remesh.py` — the script re-execs
`blender` (and `xvfb-run` when there is no `DISPLAY`).

`--help` works without Blender. `--check` confirms `bpy`.

This agent ran **Blender 4.0.2** (`bpy`) against the raw files in
`stl/`. Re-run after any OpenSCAD export (`export.sh`) so printables
stay in lockstep with the SCAD.

Last clean (no verts welded — the CGAL dumps were already watertight):

| Part | Verts | Tris | BBox mm (origin kept) |
| --- | ---: | ---: | --- |
| backlight | 1442 | 2928 | (−2, −2, 0) → (172, 74.3, 12) |
| backlight_web | 1028 | 2080 | (0.45, 0.45, 0) → (169.55, 71.85, 3.8) |
| acrylic_face | 1172 | 2372 | (0, 0, 0) → (170, 72.3, 2) |
| button_rocker | 162 | 320 | local |
| button_sel | 150 | 296 | local |
| button_trip | 150 | 296 | local |

## What the script does (per part)

One solid per file. **Tray and web stay separate** — never joined.

| Step | Why |
| --- | --- |
| mm units, 1 Blender unit = 1 mm | Matches OpenSCAD / slicers |
| Origin left at `(0, 0, 0)` | Face parts: bottom-left of the 170 × 72.3 box. Buttons: local SCAD origin (flange may extend negative). **Not** origin-to-geometry |
| Merge-by-distance `1e-4` mm | Drop double verts without moving the lock outline |
| Delete loose + dissolve degenerates | Hygiene only |
| Normals consistent, outward | Slicers / manifold checks |
| `fill_holes(sides=4)` only if non-manifold | Raw CGAL dumps were already watertight — no voxel remesh |
| No voxel / quad remesh / fair | Would chew the parabola arch (`y% = 28 u²`) and 58–72% notches |

## Exports

| Path | What |
| --- | --- |
| `print/stl/*.stl` | Cleaned binary printables (one body each) |
| `print/step/*.step` | **Faceted** millimetre STEP (tessellated `FACETED_BREP`). Blender cannot emit parametric NURBS/STEP from a mesh — this is the same triangles as the STL, not a B-rep rebuild |
| `print/obj/*.obj` | Fallback interchange if a CAD package rejects tessellated STEP |
| `preview/assembly.glb` | Exploded coloured stack (14 mm air, same as `assembly.scad`). glTF metres = mesh mm × 0.001 |

## Materials (still not a fit claim)

| Parts | Print | Do not use |
| --- | --- | --- |
| Tray, web, acrylic-mask proxy | **PETG or ASA** | **PLA** — creeps on a sun-soaked dash |
| Rocker / SEL / TRIP | TPU 95A or silicone from a printed master | PLA; do not call TPU “OEM rubber” |
| Production face | Laser acrylic | PLA |

Keep first prints as **tracing templates**. Fits stay loose until callipers.

## What this is not

- Not a verified AP1 drop-in
- Not new dimensions (do not “fix” the 170 × 72.3 lock here)
- Not a pygame / protocol change
- Not a Honda harness / connector model
