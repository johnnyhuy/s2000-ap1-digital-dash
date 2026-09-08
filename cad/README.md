# Placeholder CAD (not production)

OpenSCAD sources only. No STLs are committed — export locally if you need a
bench mock-up.

These parts are **dimensional guesses** for a Phase 1 wall-powered bench
(Pi 5 + 7" AMOLED). They are **not** AP1-accurate and must not go in the
car until the bay and connectors are measured with callipers.

## Overlay path

The factory cluster stays plugged. This bezel is an overlay / replacement
face for a display that sits in (or in front of) the bay. The legal
odometer keeps counting on the OEM cluster. Phase 1 is wall power on the
bench. Phase 2 will add high-Z taps later — these connector shells are
**not** those taps and are **not** Honda drop-ins.

## Callipers required before any cabin print

Do not print `bezel_7in_placeholder.scad` for the dash until you have
measured the real opening. Do not print the connector shells onto a
factory harness.

### Measure list

Panel / bay

- Cluster bay opening: width × height × depth, including any lip or radius
- Distance from glass plane to bay rear / harness
- AMOLED module overall: width × height × thickness (incl. PCB + stiffener)
- Active area: width × height, and offset from module edges
- Mounting hole pattern (or tape / clip points) and fastener size
- Mini-HDMI / FPC tail exit: side, width, stack height
- Sight lines / hood so the cluster does not reflect on the windscreen

Connectors (both ends)

- Pin count and row count
- **Pitch** and row spacing (unknown until callipers — the SCAD default 2.54 mm is a hobby guess)
- Pin / socket diameter and length
- Housing envelope, keying, latch, and polarizer side
- Wire gauge and strain-relief need
- Approach angle of the OEM loom (do not force a bend)

## Print notes

- **PETG or ASA** for anything that will see cabin heat.
- **Do not use PLA** in the cabin. It softens and creeps on a sun-soaked dash.
- Keep fits loose until the second measure. First prints are tracing templates.
- Export STL locally; do not commit large binaries unless they are tiny fixtures.
- Slice with enough perimeters on the bezel lip so the panel cannot punch through.

## Files

| File | What it is |
| --- | --- |
| `bezel_7in_placeholder.scad` | Frame for a ~7" landscape AMOLED (~164×100 overall / ~154×87 active placeholders) |
| `connector_male_placeholder.scad` | Generic multi-pin male shell |
| `connector_female_placeholder.scad` | Generic multi-pin female shell |

Open in [OpenSCAD](https://openscad.org/) and F6 to render after you edit the measured numbers.
