import {
  AP2_FUEL_SEGS,
  AP2_TEMP_SEGS,
  FUEL_SEGS,
  REDLINE_BLOCKS,
  TEMP_SEGS,
  MODULE_H,
  VIEW_W,
  archPoly,
  faceGeom,
  hoodPath,
  lcdPath,
  sideArchPoint,
  tachArchNormal,
  tachArchXY,
  tachBandPath,
  tachTickPath,
  type FaceGeom,
} from "@/lib/geometry";
import { SevenSeg } from "./SevenSeg";
import { DEFAULT_FACE_STYLE, type FaceStyle } from "@/lib/faceStyle";
import { type IntroPhase, revealRpm, smoothstep } from "@/lib/intro";
import { BATT_LOW_V, ECT_HOT_C, FUEL_LOW_PCT, RPM_REDLINE } from "@/lib/protocol";
import type { DisplayState } from "@/lib/mockDrive";
import { ectFrac, fuelFrac } from "@/lib/mockDrive";
import { HardwareBezel } from "./Telltales";

const AMBER = "#f08c1c";
const AMBER_HOT = "#ffb030";
const AMBER_GHOST = "#2a1808";
const AMBER_BAND = "#b05812";
const RED = "#e0241c";
const RED_LCD = "#ff261c";
const WHITE = "#f8f2e8";
const CREAM = "#eee6d6";
const DIM = "#766a58";
const TICK_MINOR_DIM = "#d68e2a";
const REDLINE_PRINT = "#ba2620";

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
      <rect x={x} y={y} width={w} height={h} rx={3} fill="#0a0302" stroke="#5a1812" strokeWidth={0.8} />
      <rect x={x} y={y} width={w} height={h} rx={3} fill="url(#lcd-door)" />
    </g>
  );
}

function TachPointer({ frac, geom }: { frac: number; geom: FaceGeom }) {
  const p = tachArchXY(frac, geom);
  const n = tachArchNormal(frac, geom);
  const px = -n.y;
  const py = n.x;
  const tipX = p.x - n.x * 24;
  const tipY = p.y - n.y * 24;
  const tailX = p.x + n.x * 5.5;
  const tailY = p.y + n.y * 5.5;
  const hot = frac >= 8 / 9;
  const col = hot ? RED : CREAM;
  return (
    <g className={hot ? "needle needle-hot" : "needle"}>
      <circle cx={p.x} cy={p.y} r={3.4} fill={hot ? RED : AMBER_HOT} />
      <polygon
        points={`${tipX},${tipY} ${p.x + px * 1.7 + n.x * 2.6},${p.y + py * 1.7 + n.y * 2.6} ${tailX},${tailY} ${p.x - px * 1.7 + n.x * 2.6},${p.y - py * 1.7 + n.y * 2.6}`}
        fill={col}
      />
      <circle cx={p.x} cy={p.y} r={1.15} fill={col} />
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
    const reached = frac <= needleFrac + 1e-6;
    const w = major ? 2.2 : 1.2;
    const len = major ? 17 : 10;
    const fill = major ? WHITE : reached ? lerpHex(AMBER, AMBER_HOT, frac) : TICK_MINOR_DIM;
    segs.push(
      <path
        key={`s${i}`}
        className={reached ? "seg-lit" : "seg-ghost"}
        d={tachTickPath(frac, w, len, geom, 2.4)}
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
    const reached = mid <= needleFrac + 1e-6;
    reds.push(
      <path
        key={`r${i}`}
        className={reached ? "seg-lit seg-red" : "seg-ghost"}
        d={tachTickPath(mid, 5.0, 24, geom, 0)}
        fill={reached ? RED : REDLINE_PRINT}
        stroke="none"
      />,
    );
  }
  const washTo = Math.min(needleFrac, redFrom);
  const wash = needleFrac > 0.012 ? tachBandPath(0, washTo, 0.6, 20, geom) : "";
  const washRed = needleFrac > redFrom ? tachBandPath(redFrom, needleFrac, 0.6, 24, geom) : "";
  const trail =
    sweepT !== undefined ? tachBandPath(Math.max(0, sweepT - 0.14), Math.max(sweepT, 0.02), 0.4, 22, geom) : "";
  const tip = needleFrac > 0.002 ? needleFrac : null;
  return (
    <g aria-hidden>
      <path d={tachBandPath(0, redFrom, 0.6, 20, geom)} fill={AMBER_BAND} stroke="none" />
      <path d={tachBandPath(redFrom, 1, 0.6, 24, geom)} fill="#5c1610" stroke="none" />
      {wash ? <path d={wash} fill={AMBER_HOT} opacity={0.42} stroke="none" /> : null}
      {washRed ? <path className="seg-lit seg-red" d={washRed} fill={RED} opacity={0.55} stroke="none" /> : null}
      {trail ? <path className="sweep-bead" d={trail} fill={AMBER_HOT} opacity={0.85} stroke="none" /> : null}
      {segs}
      {reds}
      {tip !== null ? <TachPointer frac={tip} geom={geom} /> : null}
    </g>
  );
}

function TachNumbers({ geom, dim }: { geom: FaceGeom; dim?: boolean }) {
  const unit = tachArchXY(0.05, geom);
  return (
    <g className="tach-nums">
      {Array.from({ length: 10 }, (_, i) => {
        const frac = i / 9;
        const p = tachArchXY(frac, geom);
        const n = tachArchNormal(frac, geom);
        return (
          <text
            key={i}
            className="tach-num"
            x={p.x - n.x * 20}
            y={p.y - n.y * 20}
            fontSize={14.5}
            fontWeight={600}
            fontStyle="italic"
            fill={dim ? DIM : WHITE}
            textAnchor="middle"
            dominantBaseline="middle"
          >
            {i}
          </text>
        );
      })}
      <text
        x={unit.x + 8}
        y={unit.y + 36}
        fontSize={7.5}
        fontWeight={600}
        fill={dim ? DIM : WHITE}
        textAnchor="middle"
      >
        ×1000 r/min
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
  const gap = Math.max(3, w * 0.045);
  const tickW = Math.max(6, ((w - gap * (segs - 1)) / segs) * 0.72);
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
      <text x={cx} y={geom.lcd.y + 48} textAnchor="middle" fontSize={11} fill={DIM} letterSpacing="0.22em">
        S2000  DIGITAL  DASH
      </text>
      <text x={cx} y={geom.speed.y + 8} textAnchor="middle" fontSize={46} fontWeight={700} fill={AMBER_HOT} className="ready-word">
        READY
      </text>
      <text x={cx} y={geom.speed.y + 36} textAnchor="middle" fontSize={10} fill={DIM} letterSpacing="0.12em">
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
  const { temp, fuel, speed: sc, odo, clock, module: m, step, hoodPeakY, springY, lcdPeakY, lcdSpringY, lcd } = geom;
  const lip = archPoly(m.x + step, m.x + m.w - step, hoodPeakY + 3, springY - 2);
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
            <filter id="amber-bloom" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="1.8" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <pattern id="lcd-door" width="4" height="8" patternUnits="userSpaceOnUse">
              <rect width="1" height="8" fill="rgba(255,48,32,0.1)" />
            </pattern>
          </defs>
          <path d={hoodPath(geom)} fill="#161412" stroke="#3a342e" strokeWidth="1" />
          {ap2 ? null : <polyline points={lip} fill="none" stroke="#6a6258" strokeWidth="2.1" />}
          <path d={lcdPath(geom)} fill="#090302" stroke="none" />
          <path d={lcdPath(geom)} fill="#5a320c" fillOpacity="0.16" />
          <polyline
            points={archPoly(lcd.x + 10, lcd.x + lcd.w - 10, lcdPeakY + 1.4, lcdSpringY - 5)}
            fill="none"
            stroke={CREAM}
            strokeWidth="1.35"
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
              r={9}
              fill="#ffd56a"
              filter="url(#amber-bloom)"
            />
          ) : null}

          {phase === "ready" ? <ReadyCard face={face} geom={geom} /> : null}

          {liveLike ? (
            <>
              <LcdWindow x={sc.x - 92} y={sc.y - 44} w={196} h={68} />
              <SevenSeg
                x={sc.x - 68}
                y={sc.y - 40}
                text={String(speed).padStart(3, " ")}
                ghost="188"
                digitH={58}
                color={RED_LCD}
                ghostColor="#340808"
              />
              <text x={sc.x + 62} y={sc.y + 2} fontSize={11} fontWeight={700} fill={RED_LCD} className="lcd-label">
                km/h
              </text>
              {ap2 ? (
                <text x={clock.x} y={clock.y} textAnchor="middle" fontSize={13} fontWeight={700} fill={DIM} className="lcd-label">
                  {FACE_CLOCK}
                </text>
              ) : null}
              <LcdWindow x={odo.x - 168} y={odo.y - 20} w={336} h={40} />
              <SevenSeg
                x={odo.x - 132}
                y={odo.y - 12}
                text={odoKm}
                ghost="888888"
                digitH={22}
                color={RED_LCD}
                ghostColor="#340808"
                italic={0.04}
              />
              <text
                x={odo.x + 108}
                y={odo.y - 8}
                textAnchor="middle"
                fontSize={7.5}
                fontWeight={700}
                fill={RED_LCD}
                className="lcd-label"
              >
                TRIP A
              </text>
              <SevenSeg
                x={odo.x + 78}
                y={odo.y + 0}
                text={trip}
                ghost="888.8"
                digitH={16}
                color={RED_LCD}
                ghostColor="#340808"
                italic={0.04}
              />
              {battWarn ? (
                <text x={odo.x} y={odo.y + 22} textAnchor="middle" fontSize={11} fontWeight={700} fill={RED}>
                  {`${face.batt_v.toFixed(1)}V`}
                </text>
              ) : null}
            </>
          ) : null}

          {phase !== "ready" ? (
            ap2 ? (
              <>
                <g transform={`translate(${sideArchPoint(temp, 0).x} ${sideArchPoint(temp, 0).y - 14})`} fill={hot ? RED : AMBER}>
                  <rect x="-2" y="-10" width="4" height="12" rx="1.4" fill={hot ? RED : AMBER} stroke="none" />
                  <circle cx="0" cy="5" r="4.2" fill={hot ? RED : AMBER} stroke="none" />
                </g>
                <ArchedSideGauge
                  box={temp}
                  frac={barFracEct}
                  segs={AP2_TEMP_SEGS}
                  left={{ text: "C", fill: AMBER }}
                  right={{ text: "H", fill: hot ? RED : AMBER }}
                  warnLow={false}
                  hotEnd={hot}
                />
                <g
                  transform={`translate(${sideArchPoint(fuel, 1).x} ${sideArchPoint(fuel, 1).y - 12})`}
                  fill={lowFuel ? "#e68424" : AMBER}
                >
                  <rect x="-8" y="-4" width="9" height="13" rx="1" stroke="none" />
                  <rect x="-6" y="-9" width="5" height="5" rx="0.5" stroke="none" />
                </g>
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
                <text className="tach-num" x={temp.x - 14} y={temp.y + temp.h * 0.85} fontSize={11} fontWeight={600} fill={AMBER} textAnchor="middle">
                  C
                </text>
                <text
                  className="tach-num"
                  x={temp.x + temp.w + 14}
                  y={temp.y + temp.h * 0.85}
                  fontSize={11}
                  fontWeight={600}
                  fill={hot ? RED : AMBER}
                  textAnchor="middle"
                >
                  H
                </text>
                <g transform={`translate(${temp.x + 10} ${temp.y - 12}) scale(0.55)`} fill={hot ? RED : AMBER} stroke={hot ? RED : AMBER}>
                  <rect x="-2" y="-10" width="4" height="12" rx="1.4" fill={hot ? RED : AMBER} stroke="none" />
                  <circle cx="0" cy="5" r="4.2" fill={hot ? RED : AMBER} stroke="none" />
                  <path d="M4 -8h5M4 -4h5M4 0h5M4 4h5" strokeWidth="1.4" fill="none" />
                  <path d="M-6 12c1.4-1.4 2.8 1.4 4.2 0s2.8 1.4 4.2 0 2.8 1.4 4.2 0" fill="none" strokeWidth="1.3" />
                </g>
                <SegBar {...temp} frac={barFracEct} segs={TEMP_SEGS} warnLow={false} hotEnd={hot} />

                <text
                  className="tach-num"
                  x={fuel.x - 14}
                  y={fuel.y + fuel.h * 0.85}
                  fontSize={11}
                  fontWeight={600}
                  fill={lowFuel ? RED : AMBER}
                  textAnchor="middle"
                >
                  E
                </text>
                <text className="tach-num" x={fuel.x + fuel.w + 14} y={fuel.y + fuel.h * 0.85} fontSize={11} fontWeight={600} fill={AMBER} textAnchor="middle">
                  F
                </text>
                <g
                  transform={`translate(${fuel.x + fuel.w - 8} ${fuel.y - 12}) scale(0.55)`}
                  fill={lowFuel ? "#e68424" : AMBER}
                  stroke={lowFuel ? "#e68424" : AMBER}
                >
                  <rect x="-8" y="-4" width="9" height="13" rx="1" stroke="none" />
                  <rect x="-6" y="-9" width="5" height="5" rx="0.5" stroke="none" />
                  <rect x="-5" y="-1" width="4" height="3" fill="#060402" stroke="none" />
                  <path d="M1 -1c6-4 10 0 10 6" fill="none" strokeWidth="1.5" />
                  <rect x="9" y="0" width="3" height="7" rx="0.8" stroke="none" />
                </g>
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
