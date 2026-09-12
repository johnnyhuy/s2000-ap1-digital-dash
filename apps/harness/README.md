# S2000 Digital Dash — web cluster harness

Shareable Next.js App Router demo of the OEM-geometry face (red 7-seg speed/odo, printed amber tach with a cream needle). Same frozen JSON fields as the Pi bench (`rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`, `odo_km`, optional `lamps`). Client-side mock drive — no Raspberry Pi, no ESP32.

The tach is a printed scale, not a filling LED bar. Numerals sit in the LCD well (bundled Barlow Condensed SemiBold Italic). Off telltales stay just above black so the strip still reads; cruise lights the ISO high beam. Green turn lamps pulse after the strike. Cluster type is self-hosted from `app/fonts/` (same OFL files as `assets/fonts/`). Inline ISO pictograms replace CSS masks so the lamp strip stays sharp.

**Face styles:** **AP1** (default — straight TEMP / FUEL, locked flat elevation) and **AP2** (interpretive arched side gauges). Toggle on the desk or open `/?style=ap2`. AP2 is **not** a measured plate.

**Unofficial DIY.** Not affiliated with Honda Motor Co., Ltd. Title mark is an original geometric H, not Honda trademark artwork.

## Local

```bash
cd apps/harness
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) (also `/harness`).

```bash
npm run build
npm test
```

Play / pause, **AP1 / AP2** face presets, and drive presets: **Idle**, **Cruise**, **VTEC**, **Warn**. Space skips the ID.4-style boot (sweep → READY → reveal). Telltale pictograms live in `components/LampIcons.tsx`; SVG plates in `public/icons/` still match `assets/icons/`. Current web stills: [`docs/assets/web-ap1-cruise.png`](../../docs/assets/web-ap1-cruise.png), [`web-ap1-warn.png`](../../docs/assets/web-ap1-warn.png), [`web-ap2-warn.png`](../../docs/assets/web-ap2-warn.png).

## Vercel

Create a project rooted at **`apps/harness`**.

1. [vercel.com/new](https://vercel.com/new) → import `johnnyhuy/s2000-digital-dash`
2. **Root Directory**: `apps/harness`
3. Framework preset: Next.js (auto)
4. Deploy

The Vercel project itself can be renamed to **s2000-digital-dash** for consistency; Root Directory stays `apps/harness`.

CLI from this folder:

```bash
npx vercel --yes
```

`vercel.json` in this directory sets `framework: nextjs`.
