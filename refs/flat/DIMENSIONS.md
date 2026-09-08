# AP1 face dimensions (flat / orthographic)

Lock file for the Phase 1 cluster. Percentages match the flat OEM elevation
(JDMaster face + TEMP / FUEL / bezel crops). Future UI edits should change
these numbers — not invent a new layout family.

Coordinate system:

- **Canvas** — 1920×1080, origin top-left.
- **Module** — hooded cluster. Width is 92% of the canvas; height is width /
  **2.35**. Origin of the percentages below is the **module** top-left.
- No perspective / 3D skew.

## Module (canvas)

| Item | Value |
| --- | --- |
| x | 4.0% of canvas |
| w | 92.0% of canvas |
| aspect (w:h) | **2.35:1** |
| y | centred, nudged up for the caption |

## Locked layout (percent of module)

| Item | Placement |
| --- | --- |
| Silhouette | **flat bottom**, **side notches** (4.4% step), **parabolic** top arch (`n = 2`) |
| Speed | centre **(50%, 40%)** |
| TEMP bar | horizontal C–H, origin **(7.5%, 72%)**, width 18.0%, height 2.8% |
| FUEL bar | horizontal E–F, origin **(74.5%, 72%)**, width 18.0%, height 2.8% |
| ODO / TRIP / BATT | same baseline as TEMP / FUEL (y = 72%) |
| Lamp / hardware strip | y ≈ **80.5%**, height 17.5% |
| Tach ends | ~9.5% in from LCD sides, y ≈ 66% (above TEMP / FUEL) |
| Tach peak | 50% x, y ≈ 14.5% |
| Redline | **five** thick blocks from 8 → 9 |
| Tach numerals | **inside** the tick arc |

Hardware strip, left → right:

- `−/+` rocker + brightness dial + **PUSH CANCEL**
- Dense icon lamp band (turn, HI, oil, CEL, battery, EPS, ABS, brake, airbag, fuel, fog, hot, turn)
- Blank oval + **TRIP**

TEMP is **not** a tall vertical stack. Both corner gauges are short horizontal
bars on the same y. The tach 0-mark sits above TEMP; 9 sits above FUEL.

Protocol JSON fields stay `rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`,
`odo_km`, plus the existing `lamps` keys. Extra lamp keys (`eps`, `brake`,
`airbag`) are optional and default off.

## What not to regress

- Vertical TEMP on the mid-face
- FUEL floating at mid-right, unmatched to TEMP
- Lamps as large labelled chips on the LCD
- Rounded “app chrome” pill instead of the notched hood
- Fake 3D cabin ellipses / drop-shadow skew
- Module aspect drifting off **2.35:1**
