# AP1 face dimensions (flat / orthographic)

Canonical lock for the **AP1** face style. Copied from the OEM flat elevation
(`ap1_cluster_flat`). Percentages are of the **module bounding box**, origin
top-left. The **AP2** style is a separate layout family (arched side gauges);
do not copy those percentages here.

Physical envelope (OEM face): **170 mm × 72.3 mm** → aspect **2.35:1**.

## Module on the 1920×1080 canvas

| Item | Value |
| --- | --- |
| x | 4.0% of canvas |
| w | 92.0% of canvas |
| aspect (w:h) | **2.35:1** |

## Silhouette (percent of module)

| Item | Value |
| --- | --- |
| Bottom | **flat** |
| Side notches | rectangular, **y = 58–72%**, depth 4.4% of width |
| Top arch | parabola **y% = 28 × u²**, u ∈ [−1, 1], rise **28%** |
| Arch peak | y = 0% (module top) |
| Arch spring | y = 28% |

## Face layout (percent of module)

| Item | Placement |
| --- | --- |
| Speed centre | **(50%, 40%)** — **3-digit 7-seg** (ghost `188`); units (`km/h`) to the **right** of the digits |
| ODO / TRIP | directly under the speed (~50% y): 6-digit odo + `TRIP A` `xxx.x` (ghost `888888` / `888.8`) |
| TEMP bar | **horizontal** C→H **left of the speedo** at **(8.0%, 50.5%)**, **w = 16%**, **h = 1.2%** — **6** thin coolant ticks |
| FUEL bar | **horizontal** E→F **right of the speedo** at **(76.0%, 50.5%)**, same w / h — finer tick ladder |
| TEMP icon | thermometer above **C** |
| FUEL icon | pump above **F** |
| Lamp / hardware strip | y ≈ **80.5%** |
| Tach 0–9 | printed amber band + thin ticks **normal to the parabola** (not upright bricks / not a circular fill); cream **dart** needle from the well onto the band; white italic numerals **inside the well**, below the printed band (0 and 9 drop extra so they clear the scale) |
| Redline | printed red zone **8–9** with five thick blocks |

Hardware strip, left → right:

- `−/+` rocker; brightness dial + **PUSH CANCEL** under the rocker
- OEM telltales (self-test order, after the signal pair):
  **←** (green), high beam (blue), **ABS** (amber), **BRAKE** (red),
  battery (red), oil (red), CEL (amber), immobilizer key (green),
  **MAINT REQ'D** (amber), **EPS** (amber), seatbelt (red), door (red),
  **SRS** (red), **→** (green)
- **SEL** oval + **TRIP** oval

AP1 style = these **horizontal bars flanking the speed/odo**. AP2 arched
TEMP/FUEL is a separate family — do not copy it here.

A vertical TEMP/FUEL stack was tried against a misread of the live photo
and is **erroneous**. Do not merge vertical side gauges into this lock.

Protocol JSON fields stay `rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`,
`odo_km`, plus the existing `lamps` keys.

## What not to regress

- **Vertical** TEMP / FUEL side stacks (erroneous; OEM AP1 is horizontal flanking bars)
- AP2 arched corner gauges copied onto AP1
- 45° chamfer instead of the **rectangular** 58–72% notches
- Semicircle / superellipse crown instead of **y = 28 u²**
- Units stacked under the speed
- Lamps as large labelled chips on the LCD (use OEM telltale artwork)
- Neon cyan high beam or sweep (high beam is ISO blue)
- Fake 3D cabin ellipses
- Module aspect drifting off **2.35:1**
- Tach numerals sitting **outside** the printed band (OEM AP1 puts 0–9 in the well)
