# Option 1 — replace-face printable stack

**This is not a verified AP1 drop-in.** Do not print these parts for the
car until you have measured the cluster bay **and** the OEM face with
callipers. Every critical size in the SCAD is marked `PLACEHOLDER` or
`TODO measure`. Millimetre numbers taken from
[`refs/flat/DIMENSIONS.md`](../../refs/flat/DIMENSIONS.md) are
**ESTIMATED** (170 × 72.3 mm, 2.35:1) and may be wrong on the real
plastic.

This folder is a **full face replace** (Option 1): a printable stack that
follows the locked flat OEM elevation in
[`refs/flat/DIMENSIONS.md`](../../refs/flat/DIMENSIONS.md) (PR
[#12](https://github.com/johnnyhuy/s2000-digital-dash/pull/12)). It is
**not** the overlay-only 7" bezel in `cad/bezel_7in_placeholder.scad`.

**Face lock (do not invent):** 170 × 72.3 mm, 2.35:1, flat bottom,
rectangular 58–72% notches, parabola `y% = 28 u²`. Speed centre
**(50%, 40%)**; ODO/TRIP under the speed. **TEMP** is a **horizontal**
C→H bar **left of the speedo** at **(8.0%, 50.5%)**, w = 16%, h = 1.2%,
6 thin ticks. **FUEL** is a **horizontal** E→F bar **right of the
speedo** at **(76.0%, 50.5%)**, same w/h. Vertical TEMP/FUEL stacks are
**erroneous** — they are not modelled here. Callipers are still
PLACEHOLDER; this is **not** a verified AP1 drop-in.

No connector pitch, clip pattern, or “it will just click in” claim lives
here. The generic shells in `cad/connector_*_placeholder.scad` are
unrelated bench guesses — do not mate them to a factory Honda plug.

OpenSCAD is the parametric source of truth. Committed STLs in `stl/` are
raw CGAL dumps — one body per file. The Blender clean pass lives in
[`blender_remesh.py`](blender_remesh.py); edit numbers here, not in a mesh.

## What you get

Each printable is **one solid** (meshes cleanly; Blender can remesh
without splitting bodies).

| File | Part | Material |
| --- | --- | --- |
| `backlight.scad` + `stl/backlight.stl` | Tray shell (floor, rim, face rebate, stem wells, align holes) | PETG / ASA |
| `backlight_web.scad` + `stl/backlight_web.stl` | Cowl-band light-web insert (drops on the tray floor) | PETG / ASA |
| `acrylic_face.scad` + `stl/acrylic_face.stl` | Arched mask: LCD / tach / lamp / button / align windows | PETG / ASA proxy, or laser acrylic |
| `button_rocker.scad` + `stl/button_rocker.stl` | −/+ PUSH CANCEL rocker (no stem — switch UNKNOWN) | TPU / silicone |
| `button_sel.scad` + `stl/button_sel.stl` | SEL oval (if present on the OEM face) | TPU / silicone |
| `button_trip.scad` + `stl/button_trip.stl` | TRIP oval | TPU / silicone |

Preview only (do **not** export as printables):

- `assembly.scad` — exploded stack (F5)
- `rubber_buttons.scad` — three buttons on one plate (F5)

Shared math: `dims.scad` (numbers), `outline.scad` (2D lock), `parts.scad`
(3D modules).

```bash
bash cad/replace_face/export.sh
```

## Blender handoff

See [`BLENDER.md`](BLENDER.md) for the remesh steps and material notes.

- Units: millimetres. Face-plate origin is the bottom-left of the 170 × 72.3
  bounding box. Buttons are local to the part.
- One STL = one manifold solid. Do not merge the tray and web in OpenSCAD
  or in Blender.
- Raw dumps: `stl/*.stl`. Cleaned printables: `print/stl/*.stl` plus
  faceted `print/step/*.step` (OBJ fallback in `print/obj/`). Coloured
  exploded preview: `preview/assembly.glb`.
- Re-run `blender --background --python cad/replace_face/blender_remesh.py`
  after `export.sh`. Keep this SCAD parametric — callipers will change
  the numbers.
- Stems, clips, and pin bosses are omitted on purpose (unknown hardware).
  Add them after measure, without pretending they fit.

## BOM layers (front → rear)

Driver / glass plane

1. **Rubber buttons** — TPU 95A or cast silicone. Rocker (− / +, push =
   CANCEL), SEL (blank oval, if the OEM face has it), TRIP oval.
2. **Acrylic front face** — 2 mm **PLACEHOLDER**. Laser-cut black / smoked
   / painted acrylic for a real mask, or a PETG / ASA print as a tracing
   template. Windows: arched LCD (inset `lcd_frame_mm` so the hole cannot
   breach the arch and split the mask), ten tach slots (0–9 placeholders,
   not OEM digits), lamp strip, three button holes, four align holes.
3. **Diffuser sheet** — bought 1.2 mm opal acrylic / PET **PLACEHOLDER**.
   Cut to the LCD aperture. Not a printed part.
4. **Cowl-band web** — optional PETG / ASA insert. Layout only, not optics.
5. **Backlight / backscreen tray** — PETG or ASA. Outer rim is
   `offset(wall)` around the 170 × 72.3 silhouette — a print wall, **not**
   a measured bay clip.
6. **LCD / AMOLED module** — not modelled. Pocket clearance is a guess.
   Phase 1 bench panel (Wisecoco-class 7") is a different rectangle; do
   not assume it fills this aperture.
7. **Switches / encoder under the rocker** — not modelled.

Rear / harness (out of scope — no pitch invented)

## Materials

| Part | Use | Do not use |
| --- | --- | --- |
| Tray, web, printed face proxy, any cabin-facing hard plastic | **PETG or ASA** | **PLA** — softens and creeps on a sun-soaked dash |
| Buttons | TPU 95A, or silicone from a printed master | PLA, and do not call TPU “OEM rubber” |
| Production face | Cast acrylic (laser) | PLA |
| Diffuser | Opal acrylic / PET sheet | PLA |

Keep first prints as **tracing templates**. Fits stay loose until a
second measure.

## Measure list (callipers required)

Panel / bay

- [ ] OEM face overall width × height × thickness
- [ ] Arch rise and spring points (confirm 28% / `y = 28 u²`)
- [ ] Notch y-range and depth (confirm 58–72% / 4.4% of width)
- [ ] Bay opening width × height × depth, lip, corner radius
- [ ] Glass plane to bay rear / harness
- [ ] Fastener or clip pattern and fastener size — **do not drill from this CAD**
- [ ] Sight line / hood so the stack does not reflect on the windscreen

Windows and hardware

- [ ] LCD / glass active area versus the inner aperture
- [ ] Lamp-strip envelope (telltale pack width is a placeholder)
- [ ] Rocker, SEL, TRIP centre-to-centre and outline
- [ ] Whether PUSH CANCEL is the rocker push, a separate knob, or both
- [ ] Button travel and the actual switch / encoder you will use

Stack

- [ ] Acrylic thickness
- [ ] Diffuser thickness
- [ ] LCD module thickness (PCB + stiffener)
- [ ] Alignment hole / pin locations on the real face (the four holes here are fiction)

Do **not** copy a 2.54 mm pitch or any other hobby pitch onto a Honda
connector. Measure the real plug if you ever model one.

## What this is not

- Not a verified AP1 drop-in
- Not the overlay-only 7" AMOLED bezel (`cad/bezel_7in_placeholder.scad`)
- Not a pygame / UI change (Honda’s track)
- Not a factory-harness replica
- Not optically designed (tach “channels” are layout placeholders)
- Not a finished cabin part (Blender only cleaned the placeholder mesh)

If the face geometry in `refs/flat/` moves, update `dims.scad` to match
that lock file — do not invent a new silhouette family. TEMP/FUEL must
stay **horizontal bars flanking the speedo** (see #12); do not restore
the old bottom-bar (y = 72%) or a vertical side stack.
