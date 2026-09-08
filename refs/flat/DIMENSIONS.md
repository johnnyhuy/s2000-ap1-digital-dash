# AP1 face dimensions (flat / orthographic)

Canonical lock for the Phase 1 cluster. Copied from the OEM flat elevation
(`ap1_cluster_flat`). Percentages are of the **module bounding box**, origin
top-left. Future UI edits change these numbers — they do not invent a new
layout family.

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
| Speed centre | **(50%, 40%)** — **3-digit 7-seg** (ghost `188`); units (`km/h`, `mph`) to the **right** of the digits |
| ODO / TRIP | directly under the speed (~50% y): 6-digit odo + `TRIP A` `xxx.x` (ghost `888888` / `888.8`) |
| TEMP bar | horizontal C–H at **(7.5%, 72.0%)**, **w = 18%**, **h = 3.0%** — **6** OEM coolant bars |
| FUEL bar | horizontal E–F at **(74.5%, 72.0%)**, same w / h as TEMP |
| TEMP icon | thermometer above **C** |
| FUEL icon | pump above **F** |
| Lamp / hardware strip | y ≈ **80.5%** |
| Tach 0–9 | **vertical** ticks on the parabola (not a circular fill); numerals inside the ticks |
| Redline | thick blocks **8–9** (five blocks) |

Hardware strip, left → right:

- `−/+` rocker; brightness dial + **PUSH CANCEL** under the rocker
- OEM telltales (self-test order, after the signal pair):
  **←** (green), high beam (blue), **ABS** (amber), **BRAKE** (red),
  battery (red), oil (red), CEL (amber), immobilizer key (green),
  **MAINT REQ'D** (amber), **EPS** (amber), seatbelt (red), door (red),
  **SRS** (red), **→** (green)
- **SEL** oval + **TRIP** oval

TEMP is **not** a tall vertical stack. Both corner gauges share y = 72%.

Protocol JSON fields stay `rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`,
`odo_km`, plus the existing `lamps` keys.

## What not to regress

- Vertical TEMP on the mid-face
- 45° chamfer instead of the **rectangular** 58–72% notches
- Semicircle / superellipse crown instead of **y = 28 u²**
- Units stacked under the speed
- Lamps as large labelled chips on the LCD (use OEM telltale artwork)
- Neon cyan high beam or sweep (high beam is ISO blue)
- Fake 3D cabin ellipses
- Module aspect drifting off **2.35:1**
