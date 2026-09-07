# S2000 AP1 Digital Dash — Phase 1

Bench-only overlay: fake JSON telemetry → hooded OEM-geometry gauges on a
Raspberry Pi 5 → Wisecoco-class 7" AMOLED (mini-HDMI).

The **OEM cluster stays plugged**. This display is an overlay so the factory
odometer remains the legal one. Phase 1 is **wall power** on the bench — no
ESP32, no car taps. Phase 2 will add **high-Z taps** later and emit the same
JSON over UART (`src/serial_reader.py`).

Repo: private under `johnnyhuy/s2000-ap1-digital-dash`.

## Face (AP1 OEM geometry)

Amber-on-black LCD sitting in a **hooded arched cowl** (cluster module, not a
full-bleed app chrome):

- Arched dense linear tach **0–9 ×1000**; thick **red blocks 8–9**; amber
  segments below the numerals
- Large digital speed centred under the arc (**km/h**)
- Vertical **TEMP C–H** on the left; horizontal **FUEL E–F** on the right
- **ODO / TRIP A / BATT** row
- Bottom lamp strip (`HI` is cyan when lit)
- Telemetry is lerped so the bars do not chatter at 20 Hz

Boot (ID.4-inspired, skippable with Space / `--no-intro`):

1. Welcome light sweep along the cowl
2. **READY** summary (batt / fuel / temp / odo)
3. Gauge reveal (tach self-test + lamp bulb-check)
4. Live

## Run on Pi

```bash
cd s2000-ap1-digital-dash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd src
python mock_telemetry.py | python gauge_ui.py
```

From the repo root the same pipe is
`python src/mock_telemetry.py | python src/gauge_ui.py`.

Fullscreen UI — Esc or Q to quit. `export DISPLAY=:0` if the Pi boots headless
to a desktop session.

### Flags

| Flag | What it does |
| --- | --- |
| `--windowed` | 1920×1080 window instead of fullscreen |
| `--intro` / `--no-intro` | Force or skip the boot sequence (intro is on unless `--smoke`) |
| `--smoke` | Dummy SDL, draw a few frames, exit (CI / Pi check; no live pipe needed) |
| `--screenshot DIR` | Write `01_sweep.png` … `04_live.png` into DIR |
| `--serial [PORT]` | Phase 2 UART stub (needs `pyserial`; default `/dev/ttyUSB0`) |

```bash
# Fast health check
python src/gauge_ui.py --smoke --windowed

# Regenerate reference shots (dummy SDL, no display required)
python src/gauge_ui.py --smoke --screenshot shots
```

`shots/` in this repo is optional. If the PNGs are missing, the command above
rebuilds them. Keep committed shots small; do not add huge dumps.

Stdin is newline JSON. Phase 2 UART is the same schema on `--serial`.

## Protocol (one JSON object per line)

See `src/protocol.py`.

Required: `rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`, `odo_km`

Optional: `lamps` object (`oil`, `cel`, `abs`, `turn_l`, `turn_r`, `high_beam`,
`fog`, `fuel_low`, `batt_warn`, `ect_hot`, …)

## Layout

- `src/protocol.py` — shared schema + parse/validate
- `src/mock_telemetry.py` — 20 Hz fake drive loop → stdout
- `src/gauge_ui.py` — pygame 1920×1080 OEM-geometry cluster + intro
- `src/serial_reader.py` — Phase 2 UART stub (pyserial optional)
- `cad/` — OpenSCAD placeholders (bezel + generic connector shells)
- `shots/` — optional PNG stills from `--screenshot`

## Tests / smoke

```bash
python -m unittest discover tests
python src/gauge_ui.py --smoke
```

## CAD placeholders

See `cad/README.md`. The 7" bezel and connector shells are **not**
AP1-accurate. **Bay callipers are required** before any cabin print.
Print in **PETG or ASA — not PLA**.
