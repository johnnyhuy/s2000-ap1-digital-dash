# S2000 AP1 Digital Dash — Phase 1

Bench-only: fake JSON telemetry → fullscreen gauges on Raspberry Pi 5 → Wisecoco 7" AMOLED (mini-HDMI).

No ESP32, no car taps yet. Same JSON schema Phase 2 will emit over UART.

Repo: private under `johnnyhuy/s2000-ap1-digital-dash`.

## Run on Pi

```bash
cd s2000-ap1-digital-dash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/mock_telemetry.py | python src/gauge_ui.py
```

Fullscreen UI — Esc or Q to quit. Set `export DISPLAY=:0` if needed.

## Protocol (one JSON object per line)

See `src/protocol.py`.

Required: `rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`, `odo_km`

Optional: `lamps` object (`oil`, `cel`, `abs`, `turn_l`, `turn_r`, `high_beam`, `fog`, `fuel_low`, `batt_warn`, `ect_hot`, …)

## Layout

- `src/protocol.py` — shared schema + parse/validate
- `src/mock_telemetry.py` — 20 Hz fake drive loop → stdout
- `src/gauge_ui.py` — pygame 1920×1080 fullscreen
- `src/serial_reader.py` — Phase 2 UART stub
