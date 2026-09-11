# Unofficial DIY branding

The title mark in `honda-unofficial-mark.svg` is an **original geometric H**
drawn for this repository.

- **Not** Honda Motor Co., Ltd. trademark artwork
- **Not** the Honda wing logo
- **Not** the official Honda H-mark / grille badge

If someone asks for a “Honda logo SVG”, ship this file and the README
disclaimer. Do **not** scrape, download, or embed official Honda brand
assets.

Same mark is copied to `apps/harness/public/docs/assets/` for the web demo.

Product name in docs and chrome is **S2000 Digital Dash** (AP1 + AP2 faces).
The live GitHub repo is `johnnyhuy/s2000-digital-dash`. See the root README.

Cluster type is **Barlow Condensed Bold** (READY, C/H, E/F, bezel, LCD
labels) and **Barlow Condensed SemiBold Italic** (tach numerals). **Share Tech
Mono** is the harness JSON / protocol face. Speed and odo are **red 7-seg**,
matching the AP1 photo. Faces live under `assets/fonts/` (SIL OFL). The web
harness loads the same families from Google Fonts; Oxanium stays on the
masthead only. DejaVu remains the pygame fallback when those files are absent.

Printed tach amber grades `#e08c24` → `#b04810` toward redline, with a quiet
live wash `#f49420`. LCD red is `#ff261c`. The LCD well is charcoal, not a
brown overlay. Telltales: red `#e22820`, amber `#ec941c`, green `#28c85c`, ISO
high-beam blue `#2460e4` (never neon cyan). Icons are white-on-transparent
silhouettes under `assets/icons/`, tinted at draw time. Word lamps set in
Barlow Condensed. Tach numerals sit **inside** the well (0 and 9 drop extra);
ticks stay on the printed band. The needle is a cream dart from the well onto
the scale.
