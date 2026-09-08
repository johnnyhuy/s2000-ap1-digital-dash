# AP1 web cluster harness

Shareable Next.js App Router demo of the amber OEM-geometry AP1 face. Same frozen JSON fields as the Pi bench (`rpm`, `speed_kmh`, `fuel_pct`, `ect_c`, `batt_v`, `odo_km`, optional `lamps`). Client-side mock drive — no Raspberry Pi, no ESP32.

**Unofficial DIY.** Not affiliated with Honda Motor Co., Ltd.

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

Play / pause and presets: **Idle**, **Cruise**, **VTEC**, **Warn**. Optional OEM lock images from `public/refs/` (copied from repo `refs/flat/` when present).

## Vercel

Create a project rooted at **`apps/harness`**.

1. [vercel.com/new](https://vercel.com/new) → import `johnnyhuy/s2000-ap1-digital-dash`
2. **Root Directory**: `apps/harness`
3. Framework preset: Next.js (auto)
4. Deploy

CLI from this folder:

```bash
npx vercel --yes
```

`vercel.json` in this directory sets `framework: nextjs`.
