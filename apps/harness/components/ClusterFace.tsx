import {
  AP2_FUEL_SEGS,
  AP2_TEMP_SEGS,
  FUEL_SEGS,
  REDLINE_BLOCKS,
  TACH_BAND_OUTER,
  TACH_TICK_MAJOR,
  TACH_TICK_MINOR,
  TEMP_SEGS,
  MODULE_H,
  VIEW_W,
  faceGeom,
  hoodPath,
  lcdPath,
  sideArchPoint,
  tachArchNormal,
  tachArchXY,
  tachBandPath,
  tachTickPath,
  tachNumXY,
  visorLipPoly,
  type FaceGeom,
} from "@/lib/geometry";
import { SevenSeg } from "./SevenSeg";
import { DEFAULT_FACE_STYLE, type FaceStyle } from "@/lib/faceStyle";
import { type IntroPhase, revealRpm, smoothstep } from "@/lib/intro";
import { BATT_LOW_V, ECT_HOT_C, FUEL_LOW_PCT, RPM_REDLINE } from "@/lib/protocol";
import type { DisplayState } from "@/lib/mockDrive";
import { ectFrac, fuelFrac } from "@/lib/mockDrive";
import { HardwareBezel } from "./Telltales";

const AMBER = "#f49420";
const AMBER_HOT = "#ffb838";
const AMBER_GHOST = "#2a180a";
const AMBER_BAND_LO = "#f0a028";
const AMBER_BAND_HI = "#a83810";
const RED = "#e42820";
const RED_LCD = "#ff261c";
const RED_LCD_GHOST = "#240808";
const WHITE = "#f8f2e8";
const CREAM = "#fff4dc";
const DIM = "#6e6454";
const TICK_MINOR_DIM = "#c47c28";
const REDLINE_PRINT = "#c4281c";
const COWL = "#100e0d";
const WELL = "#050302";
const TACH_NEEDLE_TIP = -4.4;
const TACH_NEEDLE_TAIL = 13.6;

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

function lerpHex(a: string, b: string, t: number): string {
  const parse = (hex: string) => [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];
  const [ar, ag, ab] = parse(a);
  const [br, bg, bb] = parse(b);
  return `rgb(${Math.round(lerp(ar, br, t))},${Math.round(lerp(ag, bg, t))},${Math.round(lerp(ab, bb, t))})`;
}

function LcdWindow({ x, y, w, h }: { x: number; y: number; w: number; h: number }) {
  return (
    <g className="lcd-window">
      <rect x={x} y={y} width={w} height={h} rx={1.6} fill="#060201" stroke="#1c0a08" strokeWidth={0.32} />
      <rect
        x={x + 0.7}
        y={y + 0.7}
        width={w - 1.4}
        height={h - 1.4}
        rx={1.1}
        fill="none"
        stroke="#120604"
        strokeWidth={0.22}
      />
      <rect x={x} y={y} width={w} height={h} rx={1.6} fill="url(#lcd-door)" />
    </g>
  );
}

function CoolantIcon({
  x,
  y,
  scale,
  fill,
}: {
  x: number;
  y: number;
  scale: number;
  fill: string;
}) {
  return (
    <g transform={`translate(${x} ${y}) scale(${scale})`} fill={fill} stroke={fill}>
      <rect x="-1.7" y="-14" width="3.4" height="16.2" rx="1.6" fill={fill} stroke="none" />
      <circle cx="0" cy="5.4" r="4.6" fill={fill} stroke="none" />
      <circle cx="0" cy="5.4" r="1.7" fill="#060402" stroke="none" />
      <path d="M5.2 -10.4h4.8M5.2 -6h4.8M5.2 -1.6h4.8M5.2 2.6h4.8" strokeWidth="1.4" fill="none" />
      <path
        d="M-8.2 12.4c2.4-2.6 4.8-2.6 7.2 0s4.8 2.6 7.2 0 4.8-2.6 7.2 0"
        fill="none"
        strokeWidth="1.45"
        strokeLinecap="round"
      />
      <path
        d="M-7 16c2.2-2.2 4.4-2.2 6.6 0s4.4 2.2 6.6 0 4.4-2.2 6.6 0"
        fill="none"
        strokeWidth="1.35"
        strokeLinecap="round"
      />
    </g>
  );
}

function PumpIcon({
  x,
  y,
  scale,
  fill,
}: {
  x: number;
  y: number;
  scale: number;
  fill: string;
}) {
  return (
    <g transform={`translate(${x} ${y}) scale(${scale})`} fill={fill} stroke={fill}>
      <rect x="-8.8" y="-4" width="10.6" height="15.4" rx="1.15" stroke="none" />
      <rect x="-6.8" y="-9.4" width="6.2" height="5.6" rx="0.55" stroke="none" />
      <rect x="-5.8" y="-0.6" width="4.6" height="3.5" fill="#060402" stroke="none" />
      <path d="M1.8 -1c6.8-4.8 11.6 0.3 11.4 7.4" fill="none" strokeWidth="1.65" strokeLinecap="round" />
      <rect x="10.4" y="1.4" width="3.3" height="8.2" rx="0.8" stroke="none" />
      <rect x="-8.8" y="11.4" width="10.6" height="1.9" rx="0.4" stroke="none" />
    </g>
  );
}

function TachPointer({ frac, geom }: { frac: number; geom: FaceGeom }) {
  const p = tachArchXY(frac, geom);
  const n = tachArchNormal(frac, geom);
  const px = -n.y;
  const py = n.x;
  const tipX = p.x + n.x * TACH_NEEDLE_TIP;
  const tipY = p.y + n.y * TACH_NEEDLE_TIP;
  const baseX = p.x + n.x * TACH_NEEDLE_TAIL;
  const baseY = p.y + n.y * TACH_NEEDLE_TAIL;
  const hot = frac >= 8 / 9;
  const col = hot ? RED : CREAM;
  const glow = hot ? RED : AMBER_HOT;
  const chevron = (half: number) =>
    [
      `${tipX},${tipY}`,
      `${baseX + px * half},${baseY + py * half}`,
      `${baseX - px * half},${baseY - py * half}`,
    ].join(" ");
  return (
    <g className={hot ? "needle needle-hot" : "needle"}>
      <polygon points={chevron(4.7)} fill="#1a120c" />
      <polygon points={chevron(3.65)} fill={glow} />
      <polygon points={chevron(2.55)} fill={col} />
    </g>
  );
}

function TachSegments({
  litFrac,
  geom,
  sweepT,
}: {
  litFrac: number;
  geom: FaceGeom;
  sweepT?: number;
}) {
  const redFrom = 8 / 9;
  const needleFrac = sweepT ?? litFrac;
  const segs = [];
  for (let i = 0; i <= 36; i += 1) {
    const frac = i / 36;
    if (frac >= redFrom - 1e-6) continue;
    const major = i % 4 === 0;
    const tick = major ? TACH_TICK_MAJOR : TACH_TICK_MINOR;
    const dist = sweepT === undefined ? 1 : Math.max(0, 1 - Math.abs(sweepT - frac) / 0.09);
    const fill = major ? WHITE : lerpHex(TICK_MINOR_DIM, AMBER_HOT, dist);
    segs.push(
      <path
        key={`s${i}`}
        className={major ? "seg-lit" : "seg-ghost"}
        d={tachTickPath(frac, tick.w, tick.len, geom, 1.1)}
        fill={fill}
        stroke="none"
      />,
    );
  }
  const reds = [];
  for (let i = 0; i < REDLINE_BLOCKS; i += 1) {
    const t0 = redFrom + (1 - redFrom) * (i / REDLINE_BLOCKS);
    const t1 = redFrom + (1 - redFrom) * ((i + 1) / REDLINE_BLOCKS);
    const mid = (t0 + t1) * 0.5;
    const reached = sweepT === undefined && mid <= needleFrac + 1e-6;
    reds.push(
      <path
        key={`r${i}`}
        className={reached ? "seg-lit seg-red" : "seg-ghost"}
        d={tachTickPath(mid, 3.6, TACH_BAND_OUTER - 1.2, geom, 0.6)}
        fill={reached ? RED : REDLINE_PRINT}
        stroke="none"
      />,
    );
  }
  const liveWash = sweepT === undefined;
  const washTo = Math.min(needleFrac, redFrom);
  const wash = liveWash && needleFrac > 0.012 ? tachBandPath(0, washTo, 0.25, TACH_BAND_OUTER, geom) : "";
  const washRed = liveWash && needleFrac > redFrom ? tachBandPath(redFrom, needleFrac, 0.25, TACH_BAND_OUTER + 1, geom) : "";
  const trail =
    sweepT !== undefined
      ? tachBandPath(Math.max(0, sweepT - 0.11), Math.max(sweepT, 0.012), 0.25, TACH_BAND_OUTER, geom)
      : "";
  const tip = needleFrac > 0.002 ? needleFrac : null;
  const printed = [];
  const slices = 48;
  for (let i = 0; i < slices; i += 1) {
    const t0 = (i / slices) * redFrom;
    const t1 = ((i + 1) / slices) * redFrom;
    printed.push(
      <path
        key={`band${i}`}
        d={tachBandPath(t0, t1, 0.25, TACH_BAND_OUTER, geom, 10)}
        fill={lerpHex(AMBER_BAND_LO, AMBER_BAND_HI, i / (slices - 1))}
        stroke="none"
      />,
    );
  }
  return (
    <g aria-hidden>
      {printed}
      <path d={tachBandPath(redFrom, 1, 0.25, TACH_BAND_OUTER + 1, geom)} fill="#941c18" stroke="none" />
      {wash ? <path d={wash} fill={AMBER_HOT} opacity={0.22} stroke="none" /> : null}
      {washRed ? <path className="seg-lit seg-red" d={washRed} fill={RED} opacity={0.34} stroke="none" /> : null}
      {trail ? <path className="sweep-bead" d={trail} fill={AMBER_HOT} opacity={0.62} stroke="none" /> : null}
      {segs}
      {reds}
      {tip !== null ? <TachPointer frac={tip} geom={geom} /> : null}
    </g>
  );
}

function TachNumbers({ geom, dim }: { geom: FaceGeom; dim?: boolean }) {
  const zero = tachNumXY(0, geom);
  const size = 20.6;
  return (
    <g className="tach-nums">
      {Array.from({ length: 10 }, (_, i) => {
        const frac = i / 9;
        const p = tachNumXY(frac, geom);
        return (
          <text
            key={i}
            className="tach-num"
            x={p.x}
            y={p.y + size * 0.34}
            fontSize={size}
            fontWeight={600}
            fontStyle="italic"
            fill={dim ? DIM : WHITE}
            textAnchor="middle"
          >
            {i}
          </text>
        );
      })}
      <text
        className="unit-label"
        x={zero.x + 28}
        y={zero.y + 16}
        fontSize={5.8}
        fontWeight={700}
        fill={dim ? DIM : WHITE}
        textAnchor="middle"
      >
        x1000 r/min
      </text>
    </g>
  );
}

function SegBar({
  x,
  y,
  w,
  h,
  frac,
  segs,
  warnLow,
  hotEnd,
}: {
  x: number;
  y: number;
  w: number;
  h: number;
  frac: number;
  segs: number;
  warnLow: boolean;
  hotEnd: boolean;
}) {
  const gap = Math.max(2, w * 0.028);
  const tickW = Math.max(6, ((w - gap * (segs - 1)) / segs) * 0.9);
  const tickH = Math.max(5, h * 0.82);
  const stride = segs > 1 ? (w - tickW) / (segs - 1) : 0;
  const lit = Math.round(frac * segs);
  return (
    <g>
      <line x1={x} y1={y + tickH + 3} x2={x + w} y2={y + tickH + 3} stroke="#4a3418" strokeWidth="0.8" />
      {Array.from({ length: segs }, (_, i) => {
        const on = i < lit;
        const last = i >= segs - 1;
        let fill = AMBER_GHOST;
        if (on && ((warnLow && i === 0) || (hotEnd && last && frac > 0.92))) fill = RED;
        else if (on) fill = AMBER;
        else if (warnLow && i === 0) fill = "#4e1010";
        return (
          <rect
            key={i}
            x={x + i * stride}
            y={y}
            width={tickW}
            height={tickH}
            rx={1}
            fill={fill}
            className={on ? "seg-lit" : "seg-ghost"}
          />
        );
      })}
    </g>
  );
}

function ArchedSideGauge({
  box,
  frac,
  segs,
  left,
  right,
  warnLow,
  hotEnd,
}: {
  box: { x: number; y: number; w: number; h: number };
  frac: number;
  segs: number;
  left: { text: string; fill: string };
  right: { text: string; fill: string };
  warnLow: boolean;
  hotEnd: boolean;
}) {
  const lit = Math.round(frac * segs);
  const tCount = 18;
  const band = [];
  const depth = 12;
  for (let i = 0; i <= tCount; i += 1) {
    const t = i / tCount;
    const a = sideArchPoint(box, t);
    const b = sideArchPoint(box, Math.min(1, t + 1 / tCount));
    const nx = b.y - a.y;
    const ny = a.x - b.x;
    const len = Math.hypot(nx, ny) || 1;
    band.push({ a, n: { x: (nx / len) * depth, y: (ny / len) * depth } });
  }
  const outer = band.map((p) => `${p.a.x},${p.a.y}`);
  const inner = band.map((p) => `${p.a.x + p.n.x},${p.a.y + p.n.y}`).reverse();
  const ghostPath = `M ${outer.join(" L ")} L ${inner.join(" L ")} Z`;
  const litCount = Math.max(2, Math.round(frac * tCount));
  const litOuter = band.slice(0, litCount + 1).map((p) => `${p.a.x},${p.a.y}`);
  const litInner = band
    .slice(0, litCount + 1)
    .map((p) => `${p.a.x + p.n.x},${p.a.y + p.n.y}`)
    .reverse();
  const litPath = frac > 0.02 ? `M ${litOuter.join(" L ")} L ${litInner.join(" L ")} Z` : "";
  const ticks = [];
  for (let i = 0; i < segs; i += 1) {
    const t0 = (i + 0.16) / segs;
    const t1 = (i + 0.84) / segs;
    const a = sideArchPoint(box, t0);
    const b = sideArchPoint(box, t1);
    const on = i < lit;
    const last = i >= segs - 1;
    let fill = AMBER_GHOST;
    if (on && ((warnLow && i === 0) || (hotEnd && last && frac > 0.92))) fill = RED;
    else if (on) fill = lerpHex(AMBER, AMBER_HOT, i / segs);
    else if (warnLow && i === 0) fill = "#4e1010";
    const nx = (b.y - a.y) * 0.34;
    const ny = (a.x - b.x) * 0.34;
    ticks.push(
      <path
        key={i}
        className={on ? "seg-lit" : "seg-ghost"}
        d={`M ${a.x} ${a.y} L ${b.x} ${b.y} L ${b.x + nx} ${b.y + ny} L ${a.x + nx} ${a.y + ny} Z`}
        fill={fill}
        stroke="none"
      />,
    );
  }
  const l = sideArchPoint(box, 0);
  const r = sideArchPoint(box, 1);
  return (
    <g>
      <path d={ghostPath} fill={AMBER_GHOST} stroke="none" />
      {litPath ? <path className="seg-lit" d={litPath} fill={AMBER} stroke="none" opacity={0.9} /> : null}
      {ticks}
      <text className="tach-num" x={l.x - 10} y={l.y + 4} fontSize={11} fontWeight={600} fill={left.fill} textAnchor="middle">
        {left.text}
      </text>
      <text className="tach-num" x={r.x + 10} y={r.y + 4} fontSize={11} fontWeight={600} fill={right.fill} textAnchor="middle">
        {right.text}
      </text>
    </g>
  );
}

function ReadyCard({ face, geom }: { face: DisplayState; geom: FaceGeom }) {
  const cx = geom.speed.x;
  const chips = [
    ["BATT", `${face.batt_v.toFixed(1)} V`],
    ["FUEL", `${face.fuel_pct.toFixed(0)} %`],
    ["TEMP", `${face.ect_c.toFixed(0)} °C`],
    ["ODO", `${Math.round(face.odo_km).toLocaleString("en-AU")} km`],
  ];
  return (
    <g className="ready-card">
      <text
        className="unit-label"
        x={cx}
        y={geom.lcd.y + 48}
        textAnchor="middle"
        fontSize={11}
        fill={DIM}
        letterSpacing="0.28em"
      >
        S2000  DIGITAL  DASH
      </text>
      <text
        x={cx}
        y={geom.speed.y + 8}
        textAnchor="middle"
        fontSize={52}
        fontWeight={700}
        fill={AMBER_HOT}
        className="ready-word"
        letterSpacing="0.1em"
      >
        READY
      </text>
      <text
        className="unit-label"
        x={cx}
        y={geom.speed.y + 38}
        textAnchor="middle"
        fontSize={10}
        fill={DIM}
        letterSpacing="0.16em"
      >
        IGNITION ON   SYSTEMS OK
      </text>
      {chips.map(([name, val], i) => {
        const x = cx - 210 + i * 140;
        const y = geom.odo.y + 8;
        return (
          <g key={name}>
            <text x={x} y={y} textAnchor="middle" fontSize={9} fill={DIM}>
              {name}
            </text>
            <text x={x} y={y + 18} textAnchor="middle" fontSize={14} fontWeight={700} fill={AMBER}>
              {val}
            </text>
          </g>
        );
      })}
    </g>
  );
}

const FACE_CLOCK = "11:03";

export function ClusterFace({
  face,
  style = DEFAULT_FACE_STYLE,
  phase = "live",
  phaseT = 1,
}: {
  face: DisplayState;
  style?: FaceStyle;
  phase?: IntroPhase;
  phaseT?: number;
}) {
  const geom = faceGeom(style);
  const liveLike = phase === "live" || phase === "reveal";
  const rpm = phase === "reveal" ? revealRpm(phaseT, face.rpm) : liveLike ? face.rpm : 0;
  const litFrac = Math.max(0, Math.min(1, rpm / RPM_REDLINE));
  const hot = face.ect_c >= ECT_HOT_C;
  const lowFuel = face.fuel_pct < FUEL_LOW_PCT;
  const battWarn = face.batt_v < BATT_LOW_V || Boolean(face.lamps.batt_warn);
  const speed = Math.round(Math.max(0, Math.min(399, face.speed_kmh)));
  const { temp, fuel, speed: sc, odo, clock } = geom;
  const ap2 = style === "ap2";
  const styleName = ap2 ? "AP2" : "AP1";
  const bulbCheck = phase === "reveal" && phaseT < 0.55;
  const sweepT = phase === "sweep" ? smoothstep(phaseT) : undefined;
  const sweep = sweepT !== undefined ? tachArchXY(sweepT, geom) : null;
  const barFracEct = liveLike ? ectFrac(face.ect_c) : 0;
  const barFracFuel = liveLike ? fuelFrac(face.fuel_pct) : 0;

  const odoKm = String(Math.round(face.odo_km) % 1_000_000).padStart(6, "0");
  const trip = face.trip_km.toFixed(1).padStart(5, "0");

  return (
    <figure className={`cluster cluster-${style} cluster-${phase}`}>
      <div className="cluster-stage">
        <svg
          viewBox={`0 0 ${VIEW_W} ${MODULE_H}`}
          role="img"
          aria-label={`${styleName} cluster, ${speed} kilometres per hour, ${Math.round(rpm)} rpm`}
        >
          <defs>
            <filter id="amber-bloom" x="-40%" y="-40%" width="180%" height="180%">
              <feGaussianBlur stdDeviation="1.6" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="lcd-bloom" x="-28%" y="-28%" width="156%" height="156%">
              <feGaussianBlur stdDeviation="1.35" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <pattern id="lcd-door" width="3" height="8" patternUnits="userSpaceOnUse">
              <rect width="1" height="8" fill="rgba(255,42,28,0.045)" />
            </pattern>
          </defs>
          <path d={hoodPath(geom)} fill={COWL} stroke="#3a342e" strokeWidth="1" />
          <path d={lcdPath(geom)} fill={WELL} stroke="none" />
          <path d={lcdPath(geom)} fill="#24140a" fillOpacity="0.05" />
          <polyline
            points={visorLipPoly(geom)}
            fill="none"
            stroke="#efe6d6"
            strokeWidth="1.15"
            strokeLinecap="round"
          />

          {phase !== "ready" ? (
            <>
              <TachSegments litFrac={litFrac} geom={geom} sweepT={sweepT} />
              <TachNumbers geom={geom} dim={phase === "sweep"} />
            </>
          ) : null}

          {sweep ? (
            <circle
              className="sweep-bead"
              cx={sweep.x}
              cy={sweep.y}
              r={3.2}
              fill="#ffd56a"
              filter="url(#amber-bloom)"
            />
          ) : null}

          {phase === "ready" ? <ReadyCard face={face} geom={geom} /> : null}

          {liveLike ? (
            <>
              <LcdWindow x={sc.x - 84} y={sc.y - 34} w={178} h={54} />
              <g filter="url(#lcd-bloom)">
                <SevenSeg
                  x={sc.x - 62}
                  y={sc.y - 30}
                  text={String(speed).padStart(3, " ")}
                  ghost="188"
                  digitH={50}
                  color={RED_LCD}
                  ghostColor={RED_LCD_GHOST}
                  italic={0.07}
                />
              </g>
              <text x={sc.x + 64} y={sc.y + 8} fontSize={9} fontWeight={700} fill={RED_LCD} className="lcd-label">
                km/h
              </text>
              {ap2 ? (
                <text x={clock.x} y={clock.y} textAnchor="middle" fontSize={13} fontWeight={700} fill={DIM} className="lcd-label">
                  {FACE_CLOCK}
                </text>
              ) : null}
              <LcdWindow x={odo.x - 160} y={odo.y - 16} w={320} h={34} />
              <g filter="url(#lcd-bloom)">
                <SevenSeg
                  x={odo.x - 126}
                  y={odo.y - 10}
                  text={odoKm}
                  ghost="888888"
                  digitH={20}
                  color={RED_LCD}
                  ghostColor={RED_LCD_GHOST}
                  italic={0.04}
                />
              </g>
              <text
                x={odo.x + 108}
                y={odo.y - 9}
                textAnchor="middle"
                fontSize={7.2}
                fontWeight={700}
                fill={RED_LCD}
                className="lcd-label"
              >
                TRIP A
              </text>
              <g filter="url(#lcd-bloom)">
                <SevenSeg
                  x={odo.x + 78}
                  y={odo.y + 0}
                  text={trip}
                  ghost="888.8"
                  digitH={16}
                  color={RED_LCD}
                  ghostColor={RED_LCD_GHOST}
                  italic={0.04}
                />
              </g>
              {battWarn ? (
                <text x={odo.x} y={odo.y + 24} textAnchor="middle" fontSize={11} fontWeight={700} fill={RED}>
                  {`${face.batt_v.toFixed(1)}V`}
                </text>
              ) : null}
            </>
          ) : null}

          {phase !== "ready" ? (
            ap2 ? (
              <>
                <CoolantIcon
                  x={sideArchPoint(temp, 0).x}
                  y={sideArchPoint(temp, 0).y - 16}
                  scale={0.52}
                  fill={hot ? RED : AMBER}
                />
                <ArchedSideGauge
                  box={temp}
                  frac={barFracEct}
                  segs={AP2_TEMP_SEGS}
                  left={{ text: "C", fill: AMBER }}
                  right={{ text: "H", fill: hot ? RED : AMBER }}
                  warnLow={false}
                  hotEnd={hot}
                />
                <PumpIcon
                  x={sideArchPoint(fuel, 1).x}
                  y={sideArchPoint(fuel, 1).y - 14}
                  scale={0.52}
                  fill={lowFuel ? "#e68424" : AMBER}
                />
                <ArchedSideGauge
                  box={fuel}
                  frac={barFracFuel}
                  segs={AP2_FUEL_SEGS}
                  left={{ text: "E", fill: lowFuel ? RED : AMBER }}
                  right={{ text: "F", fill: AMBER }}
                  warnLow={lowFuel}
                  hotEnd={false}
                />
              </>
            ) : (
              <>
                <text className="unit-label" x={temp.x - 14} y={temp.y + temp.h * 0.72} fontSize={11} fontWeight={700} fill={AMBER} textAnchor="middle">
                  C
                </text>
                <text
                  className="unit-label"
                  x={temp.x + temp.w + 14}
                  y={temp.y + temp.h * 0.72}
                  fontSize={11}
                  fontWeight={700}
                  fill={hot ? RED : AMBER}
                  textAnchor="middle"
                >
                  H
                </text>
                <CoolantIcon x={temp.x + 10} y={temp.y - 16} scale={0.62} fill={hot ? RED : AMBER} />
                <SegBar {...temp} frac={barFracEct} segs={TEMP_SEGS} warnLow={false} hotEnd={hot} />

                <text
                  className="unit-label"
                  x={fuel.x - 14}
                  y={fuel.y + fuel.h * 0.72}
                  fontSize={11}
                  fontWeight={700}
                  fill={lowFuel ? RED : AMBER}
                  textAnchor="middle"
                >
                  E
                </text>
                <text className="unit-label" x={fuel.x + fuel.w + 14} y={fuel.y + fuel.h * 0.72} fontSize={11} fontWeight={700} fill={AMBER} textAnchor="middle">
                  F
                </text>
                <PumpIcon x={fuel.x + fuel.w - 8} y={fuel.y - 16} scale={0.62} fill={lowFuel ? "#e68424" : AMBER} />
                <SegBar {...fuel} frac={barFracFuel} segs={FUEL_SEGS} warnLow={lowFuel} hotEnd={false} />
              </>
            )
          ) : null}
        </svg>
        <HardwareBezel
          lamps={phase === "sweep" || phase === "ready" ? {} : face.lamps}
          battV={phase === "sweep" || phase === "ready" ? 14 : face.batt_v}
          selLabel={ap2 ? "CLOCK" : "SEL"}
          bulbCheck={bulbCheck}
        />
      </div>
      <figcaption className="cluster-caption">{styleName}</figcaption>
    </figure>
  );
}
