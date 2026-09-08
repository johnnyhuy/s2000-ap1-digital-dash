# AP1 face dimensions (flat / orthographic)

Lock file for the Phase 1 cluster. Percentages are taken from the OEM AP1
JDMaster face photo plus the bottom-left TEMP, bottom-right FUEL, and lower
bezel crops. Future UI edits should change these numbers — not invent new
layout families.

Coordinate system:

- **Canvas** — 1920×1080, origin top-left.
- **Module** — hooded cluster, percent of the canvas.
- **LCD** — inner aperture bounding box (arched top, **flat bottom**), percent
  of that box unless noted.
- No perspective / 3D skew. The physical cluster is drawn as a flat elevation.

## Module (percent of canvas)

| Item | x | y | w | h |
| --- | --- | --- | --- | --- |
| Module | 4.0% | 16.8% | 92.0% | 66.2% |

| Item | % of module |
| --- | --- |
| Side step (45° inward, each side) | 4.4% of width |
| Hardware / lamp bezel height | 17.5% of height |
| LCD top (inner arch peak) | 14.5% from module top |
| Gap, LCD bottom → bezel | 1.8% of height |
| Outer arch exponent `n` | 3.25 (superellipse; flatter crown, steeper sides) |

Silhouette rules (OEM housing):

1. **Flat bottom** — both lower corners share the same y.
2. **Stepped sides** — short vertical rise (bezel), 45° inward step, then
   vertical LCD sides that meet the arch.
3. **Broad top arch** — not a semicircle; crown is flatter than the sides.

LCD aperture aspect is about **3.5:1** (wide, short). Do not let the well
become a tall rounded rectangle.

## LCD face (percent of LCD bounding box)

| Item | Placement |
| --- | --- |
| Tach 0 / 9 ends | 10.0% in from each side, **68%** down |
| Tach peak | 50% x, **5.0%** down |
| Tach numbers | **inside** the tick arc (smaller radius than the blocks) |
| Redline | **five** thick blocks from 8 → 9 (`8/9` … `1.0`) |
| `x1000r/min` | under the 0–1 ticks, lower left |
| Speed | 50% x, **50%** down, centred in the tach bowl |
| ODO / TRIP / BATT | 50% x, **85.5%** down — **same baseline** as TEMP / FUEL |
| TEMP bar | horizontal **C–H**, 1.8% from left, width 20.5%, y **88%**, h 4.2% |
| FUEL bar | horizontal **E–F**, 1.8% from right, **same y / h / width** as TEMP |
| TEMP icon | thermometer above the **C** end |
| FUEL icon | pump above the **F** end |

TEMP is **not** a tall vertical stack on the mid-left. Both corner gauges are
short horizontal bars sitting on the flat LCD bottom, with the tach 0-mark
above TEMP and the 9-mark above FUEL.

## Hardware strip (below the LCD, on the bezel)

Percent of **module** width, vertically centred in the 17.5% bezel band:

| Item | Placement |
| --- | --- |
| − / + rocker | left, pill, ~9.2% wide |
| Brightness dial + `PUSH CANCEL` | immediately right of the rocker |
| Lamp band | dark translucent strip, packed **icons** (not sparse text chips) |
| Blank oval + `TRIP` | right pair, ~6.2% wide each |

Lamp order (left → right): turn L, high beam, oil, CEL / engine, battery,
EPS, ABS, brake, airbag, low fuel, fog, hot, turn R.

Protocol JSON fields stay `rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`,
`odo_km`, plus the existing `lamps` keys. Extra lamp keys (`eps`, `brake`,
`airbag`) are optional and default off.

## What not to regress

- Vertical TEMP on the mid-face
- FUEL floating at mid-right, unmatched to TEMP
- Lamps drawn as large labelled chips on the LCD with a hollow gap under the
  speed
- Rounded “app chrome” pill instead of the stepped hood
- Fake 3D cabin ellipses / drop-shadow skew

