# S2000 AP1 Digital Dash — Phase 1

Bench-only overlay: fake JSON telemetry → fullscreen gauges on a Raspberry Pi 5
→ Wisecoco-class 7" AMOLED (mini-HDMI).

The **OEM cluster stays plugged**. This display is an overlay so the factory
odometer remains the legal one. Phase 1 is **wall power** on the bench — no
ESP32, no car taps. Phase 2 will add **high-Z taps** later and emit the same
JSON over UART (`src/serial_reader.py`).

Repo: private under `johnnyhuy/s2000-ap1-digital-dash`.

## Run on Pi

```bash
cd s2000-ap1-digital-dash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd src
python mock_telemetry.py | python gauge_ui.py
```

From the repo root the same pipe is `python src/mock_telemetry.py | python src/gauge_ui.py`.

Fullscreen UI — Esc or Q to quit. `export DISPLAY=:0` if the Pi boots headless
to a desktop session.

Useful flags on `gauge_ui.py`:

| Flag | What it does |
| --- | --- |
| `--windowed` | 1920×1080 window instead of fullscreen |
| `--smoke` | Draw a few dummy frames and exit (no live pipe needed) |
| `--serial [PORT]` | Phase 2 UART stub (needs `pyserial`; default `/dev/ttyUSB0`) |

```bash
python src/gauge_ui.py --smoke --windowed
```

## Protocol (one JSON object per line)

See `src/protocol.py`.

Required: `rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`, `odo_km`

Optional: `lamps` object (`oil`, `cel`, `abs`, `turn_l`, `turn_r`, `high_beam`,
`fog`, `fuel_low`, `batt_warn`, `ect_hot`, …)

## Layout

- `src/protocol.py` — shared schema + parse/validate
- `src/mock_telemetry.py` — 20 Hz fake drive loop → stdout
- `src/gauge_ui.py` — pygame 1920×1080 AP1-ish digital cluster
- `src/serial_reader.py` — Phase 2 UART stub (pyserial optional)
- `cad/` — OpenSCAD placeholders (bezel + generic connector shells)

## CAD placeholders

See `cad/README.md`. The 7" bezel and connector shells are **not**
AP1-accurate. **Bay callipers are required** before any cabin print.
Print in **PETG or ASA — not PLA**.
