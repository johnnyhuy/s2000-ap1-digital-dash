# Option 1 — replace-face printable stack

**This is not a verified AP1 drop-in.** Do not print these parts for the
car until you have measured the cluster bay **and** the OEM face with
callipers. Every critical size in the SCAD is marked `PLACEHOLDER` or
`TODO measure`. Millimetre numbers taken from
[`refs/flat/DIMENSIONS.md`](../../refs/flat/DIMENSIONS.md) are
**ESTIMATED** (170 × 72.3 mm, 2.35:1) and may be wrong on the real
plastic.

This folder is a **full face replace** (Option 1): a printable stack that
follows the locked flat OEM elevation. It is **not** the overlay-only 7"
bezel in `cad/bezel_7in_placeholder.scad`.

No connector pitch, clip pattern, or “it will just click in” claim lives
here. The generic shells in `cad/connector_*_placeholder.scad` are
unrelated bench guesses — do not mate them to a factory Honda plug.

## What you get

| File | Part |
| --- | --- |
| `backlight.scad` + `stl/backlight.stl` | Rear light tray / diffuser frame (backscreen) |
| `acrylic_face.scad` + `stl/acrylic_face.stl` | Arched mask: LCD window, tach slot placeholders, lamp window, button holes |
| `rubber_buttons.scad` + `stl/rubber_buttons.stl` | −/+ PUSH CANCEL rocker, SEL oval, TRIP oval |
| `assembly.scad` + `stl/assembly.stl` | Stacked preview (explode = 14 mm). Not a printable fit check. |

Shared math: `dims.scad` (numbers), `outline.scad` (2D lock), `parts.scad`
(3D modules). Open `assembly.scad` in [OpenSCAD](https://openscad.org/)
and F5 to preview. F6 each part file before you trust an export.

Regenerate STLs:

```bash
bash cad/replace_face/export.sh
```

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
   Cut to the LCD rebate. Not a printed part; the tray only holds it.
4. **Backlight / backscreen tray** — PETG or ASA. Floor + rim + cowl-band
   light web + lamp well + stem wells + face rebate. Outer rim is
   `offset(wall)` around the 170 × 72.3 silhouette — a print wall, **not**
   a measured bay clip.
5. **LCD / AMOLED module** — not modelled. Pocket clearance is a guess.
   Phase 1 bench panel (Wisecoco-class 7") is a different rectangle; do
   not assume it fills this aperture.
6. **Switches / encoder under the rocker** — not modelled. Stem diameter
   and travel are fiction until you pick a switch.

Rear / harness (out of scope — no pitch invented)

## Materials

| Part | Use | Do not use |
| --- | --- | --- |
| Tray, printed face proxy, any cabin-facing hard plastic | **PETG or ASA** | **PLA** — softens and creeps on a sun-soaked dash |
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
- [ ] Alignment pin locations on the real face (the four pins here are fiction)

Do **not** copy a 2.54 mm pitch or any other hobby pitch onto a Honda
connector. Measure the real plug if you ever model one.

## What this is not

- Not a verified AP1 drop-in
- Not the overlay-only 7" AMOLED bezel (`cad/bezel_7in_placeholder.scad`)
- Not a pygame / UI change (Honda’s track)
- Not a factory-harness replica
- Not optically designed (tach “channels” are layout placeholders)

If the face geometry in `refs/flat/` moves, update `dims.scad` to match
that lock file — do not invent a new silhouette family.
