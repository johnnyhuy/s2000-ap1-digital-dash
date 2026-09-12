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
harness self-hosts the same OFL files from `apps/harness/app/fonts/`; Oxanium
stays on the masthead only. DejaVu remains the pygame fallback when those
files are absent.

Printed tach amber grades `#f0a028` → `#a83810` toward redline in 48 slices,
with a quiet live wash `#f49420`. The web face keeps the printed scale and
a short cream chevron needle (not a filling LED bar). LCD red is `#ff261c`
with a readable 188 / 888888 ghost (`#240808` on the web face, `#240808` in
pygame). The LCD well is charcoal with a faint screen-door, not a brown
overlay. Telltales: red `#e22820`, amber `#ec941c`, green `#28cc5c`, ISO
high-beam blue `#2460e4` (never neon cyan). Off lamps sit just above black
(`#322e2a` on the web strip, `#2c2824` in pygame) so the row still reads
without competing with lit bulbs. Icons are white-on-transparent ISO
silhouettes (hollow battery with +/−, oil-can with drop, 3-ray outlined
high-beam D, CEL with CHECK punched through the block, filled key bow,
person with sash, top-down car with both doors ajar) under `assets/icons/`,
tinted at draw time. The web strip draws the same pictograms inline
(`LampIcons.tsx`) so CSS masks cannot collapse them. Word lamps set in
Barlow Condensed. Tach numerals sit **inside** the well (0 and 9 drop extra)
in Barlow Condensed SemiBold Italic with tight-but-not-crushed tracking.
Ticks stay on the printed band. Analog lag on RPM; green turn lamps pulse
at about 85 flashes/min after the strike. Boot motion is sweep comet →
READY glow → reveal settle. Preset buttons on the web harness snap the
face so Idle / Cruise / VTEC / Warn are readable immediately.
