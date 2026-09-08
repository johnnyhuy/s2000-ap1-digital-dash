import {
  AP2_FUEL_SEGS,
  AP2_TEMP_SEGS,
  FUEL_SEGS,
  REDLINE_BLOCKS,
  TEMP_SEGS,
  VIEW_H,
  VIEW_W,
  archPoly,
  faceGeom,
  hoodPath,
  lcdPath,
  sideArchPoint,
  tachArchNormal,
  tachArchXY,
  tachTickPath,
  type FaceGeom,
} from "@/lib/geometry";
import { SevenSeg } from "./SevenSeg";
import { DEFAULT_FACE_STYLE, type FaceStyle } from "@/lib/faceStyle";
import { BATT_LOW_V, ECT_HOT_C, FUEL_LOW_PCT, RPM_REDLINE } from "@/lib/protocol";
import type { DisplayState } from "@/lib/mockDrive";
import { ectFrac, fuelFrac } from "@/lib/mockDrive";
import { TelltaleStrip } from "./Telltales";

const AMBER = "#ec9820";
const AMBER_HOT = "#ffb02e";
const AMBER_GHOST = "#281a0a";
const AMBER_WASH = "#34260c";
const RED = "#d6241e";
const RED_GHOST = "#2a0e0c";
const WHITE = "#e6e2d6";
const DIM = "#5c5446";

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
  const r = Math.round(lerp(ar, br, t));
  const g = Math.round(lerp(ag, bg, t));
  const bl = Math.round(lerp(ab, bb, t));
  return `rgb(${r},${g},${bl})`;
}

function TachSegments({ litFrac, geom }: { litFrac: number; geom: FaceGeom }) {
  const redFrom = 8 / 9;
  const minors = 36;
  const wash = [];
  for (let i = 0; i < 28; i += 1) {
    wash.push(
      <path key={`w${i}`} d={tachTickPath(i / 27, 1.6, 18, geom)} fill={AMBER_WASH} />,
    );
  }
  const segs = [];
  for (let i = 0; i <= minors; i += 1) {
    const frac = i / minors;
    if (frac >= redFrom - 1e-6) continue;
    const major = i % 4 === 0;
    const on = frac <= litFrac + 1e-6;
    const w = major ? 1.7 : 1.05;
    const len = major ? 20 : 12;
    segs.push(
      <path
        key={`s${i}`}
        className={on ? "seg-lit" : undefined}
        d={tachTickPath(frac, w, len, geom)}
        fill={on ? (major ? WHITE : lerpHex(AMBER, AMBER_HOT, frac)) : major ? "#3a3024" : AMBER_GHOST}
      />,
    );
  }
  const reds = [];
  for (let i = 0; i < REDLINE_BLOCKS; i += 1) {
    const t0 = redFrom + (1 - redFrom) * (i / REDLINE_BLOCKS);
    const t1 = redFrom + (1 - redFrom) * ((i + 1) / REDLINE_BLOCKS);
    const mid = (t0 + t1) * 0.5;
    const on = mid <= litFrac + 1e-6;
    reds.push(
      <path
        key={`r${i}`}
        className={on ? "seg-lit" : undefined}
        d={tachTickPath(mid, 3.6, 26, geom, 0)}
        fill={on ? RED : RED_GHOST}
      />,
    );
  }
  return (
    <g aria-hidden>
      {wash}
      {segs}
      {reds}
    </g>
  );
}

function TachNumbers({ geom }: { geom: FaceGeom }) {
  return (
    <g className="tach-nums">
      {Array.from({ length: 10 }, (_, i) => {
        const hot = i >= 8;
        const frac = i / 9;
        const p = tachArchXY(frac, geom);
        const n = tachArchNormal(frac, geom);
        const x = p.x - n.x * 14;
        const y = p.y - n.y * 14;
        return (
          <text
            key={i}
            x={x}
            y={y}
            fill={hot ? RED : AMBER}
            textAnchor="middle"
            dominantBaseline="middle"
          >
            {i}
          </text>
        );
      })}
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
  const tickH = Math.max(3.2, Math.min(5.5, h));
  const gap = Math.max(3, w * 0.045);
  const tickW = Math.max(7, ((w - gap * (segs - 1)) / segs) * 0.7);
  const stride = segs > 1 ? (w - tickW) / (segs - 1) : 0;
  const lit = Math.round(frac * segs);
  return (
    <g>
      <line x1={x} y1={y + tickH + 2} x2={x + w} y2={y + tickH + 2} stroke="#4e3210" strokeWidth="1" />
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
            rx={0.6}
            fill={fill}
            className={on ? "seg-lit" : undefined}
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
  const ticks = [];
  for (let i = 0; i < segs; i += 1) {
    const t0 = (i + 0.12) / segs;
    const t1 = (i + 0.88) / segs;
    const a = sideArchPoint(box, t0);
    const b = sideArchPoint(box, t1);
    const on = i < lit;
    const last = i >= segs - 1;
    let fill = AMBER_GHOST;
    if (on && ((warnLow && i === 0) || (hotEnd && last && frac > 0.92))) fill = RED;
    else if (on) fill = lerpHex(AMBER, AMBER_HOT, i / segs);
    else if (warnLow && i === 0) fill = "#4e1010";
    const nx = (b.y - a.y) * 0.22;
    const ny = (a.x - b.x) * 0.22;
    ticks.push(
      <path
        key={i}
        className={on ? "seg-lit" : undefined}
        d={`M ${a.x} ${a.y} L ${b.x} ${b.y} L ${b.x + nx} ${b.y + ny} L ${a.x + nx} ${a.y + ny} Z`}
        fill={fill}
      />,
    );
  }
  const l = sideArchPoint(box, 0);
  const r = sideArchPoint(box, 1);
  return (
    <g>
      {ticks}
      <text x={l.x - 10} y={l.y + 4} className="tiny" fill={left.fill} textAnchor="middle">
        {left.text}
      </text>
      <text x={r.x + 10} y={r.y + 4} className="tiny" fill={right.fill} textAnchor="middle">
        {right.text}
      </text>
    </g>
  );
}

const FACE_CLOCK = "11:03";

export function ClusterFace({
  face,
  style = DEFAULT_FACE_STYLE,
}: {
  face: DisplayState;
  style?: FaceStyle;
}) {
  const geom = faceGeom(style);
  const litFrac = Math.max(0, Math.min(1, face.rpm / RPM_REDLINE));
  const hot = face.ect_c >= ECT_HOT_C;
  const lowFuel = face.fuel_pct < FUEL_LOW_PCT;
  const battWarn = face.batt_v < BATT_LOW_V || Boolean(face.lamps.batt_warn);
  const speed = Math.round(Math.max(0, Math.min(399, face.speed_kmh)));
  const { temp, fuel, speed: sc, odo, clock, module: m, step, hoodPeakY, springY } = geom;
  const lip = archPoly(m.x + step, m.x + m.w - step, hoodPeakY + 3, springY - 2);
  const ap2 = style === "ap2";
  const styleName = ap2 ? "AP2" : "AP1";

  return (
    <figure className={`cluster cluster-${style}`}>
      <svg
        viewBox={`-8 -6 ${VIEW_W + 16} ${VIEW_H}`}
        role="img"
        aria-label={`${styleName} cluster, ${speed} kilometres per hour, ${Math.round(face.rpm)} rpm`}
      >
        <defs>
          <filter id="amber-bloom" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path d={hoodPath(geom)} fill="#1a1918" stroke="#3a342c" strokeWidth="1.6" />
        <polyline points={lip} fill="none" stroke="#2c2824" strokeWidth="2.2" />
        <path d={lcdPath(geom)} fill="#120c06" stroke="#241810" strokeWidth="1.2" />
        <TachSegments litFrac={litFrac} geom={geom} />
        <TachNumbers geom={geom} />

        <foreignObject x={sc.x - 92} y={sc.y - 38} width="200" height="80">
          <SevenSeg
            text={String(speed).padStart(3, " ")}
            ghost="188"
            digitH={68}
            color="#ffb02e"
            ghostColor="#281a0a"
          />
        </foreignObject>
        <text x={sc.x + 96} y={sc.y + 6} className="unit" fill={AMBER}>
          km/h
        </text>
        {ap2 ? (
          <text x={clock.x} y={clock.y} textAnchor="middle" className="odo" fill={DIM}>
            {FACE_CLOCK}
          </text>
        ) : null}
        <text x={odo.x} y={odo.y} textAnchor="middle" className="odo" fill={AMBER} filter="url(#amber-bloom)">
          {`ODO  ${String(Math.round(face.odo_km) % 1_000_000).padStart(6, "0")}    TRIP A  ${face.trip_km.toFixed(1).padStart(5, "0")}`}
        </text>
        {battWarn ? (
          <text x={odo.x + 210} y={odo.y - 16} className="batt" fill={RED}>
            {`${face.batt_v.toFixed(1)}V`}
          </text>
        ) : null}

        {ap2 ? (
          <>
            <g transform={`translate(${temp.x + 18} ${temp.y + 6})`} fill={hot ? RED : AMBER} stroke={hot ? RED : AMBER}>
              <rect x="-2" y="-10" width="4" height="12" rx="1.4" fill={hot ? RED : AMBER} stroke="none" />
              <circle cx="0" cy="5" r="4.2" fill={hot ? RED : AMBER} stroke="none" />
            </g>
            <ArchedSideGauge
              box={temp}
              frac={ectFrac(face.ect_c)}
              segs={AP2_TEMP_SEGS}
              left={{ text: "C", fill: AMBER }}
              right={{ text: "H", fill: hot ? RED : AMBER }}
              warnLow={false}
              hotEnd={hot}
            />
            <g
              transform={`translate(${fuel.x + fuel.w - 18} ${fuel.y + 8})`}
              fill={lowFuel ? "#e68424" : AMBER}
              stroke={lowFuel ? "#e68424" : AMBER}
            >
              <rect x="-8" y="-4" width="9" height="13" rx="1" stroke="none" />
              <rect x="-6" y="-9" width="5" height="5" rx="0.5" stroke="none" />
            </g>
            <ArchedSideGauge
              box={fuel}
              frac={fuelFrac(face.fuel_pct)}
              segs={AP2_FUEL_SEGS}
              left={{ text: "E", fill: lowFuel ? RED : AMBER }}
              right={{ text: "F", fill: AMBER }}
              warnLow={lowFuel}
              hotEnd={false}
            />
          </>
        ) : (
          <>
            <text x={temp.x - 14} y={temp.y + temp.h * 0.85} className="tiny" fill={AMBER} textAnchor="middle">
              C
            </text>
            <text x={temp.x + temp.w + 14} y={temp.y + temp.h * 0.85} className="tiny" fill={hot ? RED : AMBER} textAnchor="middle">
              H
            </text>
            <g transform={`translate(${temp.x + 8} ${temp.y - 18})`} fill={hot ? RED : AMBER} stroke={hot ? RED : AMBER}>
              <rect x="-2" y="-10" width="4" height="12" rx="1.4" fill={hot ? RED : AMBER} stroke="none" />
              <circle cx="0" cy="5" r="4.2" fill={hot ? RED : AMBER} stroke="none" />
              <path d="M4 -8h5M4 -4h5M4 0h5M4 4h5" strokeWidth="1.4" fill="none" />
              <path d="M-6 12c1.4-1.4 2.8 1.4 4.2 0s2.8 1.4 4.2 0 2.8 1.4 4.2 0" fill="none" strokeWidth="1.3" />
              <path d="M-6 16c1.4-1.4 2.8 1.4 4.2 0s2.8 1.4 4.2 0 2.8 1.4 4.2 0" fill="none" strokeWidth="1.3" />
              <path d="M-6 20c1.4-1.4 2.8 1.4 4.2 0s2.8 1.4 4.2 0 2.8 1.4 4.2 0" fill="none" strokeWidth="1.3" />
            </g>
            <SegBar {...temp} frac={ectFrac(face.ect_c)} segs={TEMP_SEGS} warnLow={false} hotEnd={hot} />

            <text x={fuel.x - 14} y={fuel.y + fuel.h * 0.85} className="tiny" fill={lowFuel ? RED : AMBER} textAnchor="middle">
              E
            </text>
            <text x={fuel.x + fuel.w + 14} y={fuel.y + fuel.h * 0.85} className="tiny" fill={AMBER} textAnchor="middle">
              F
            </text>
            <g
              transform={`translate(${fuel.x + fuel.w - 6} ${fuel.y - 16})`}
              fill={lowFuel ? "#e68424" : AMBER}
              stroke={lowFuel ? "#e68424" : AMBER}
            >
              <rect x="-8" y="-4" width="9" height="13" rx="1" stroke="none" />
              <rect x="-6" y="-9" width="5" height="5" rx="0.5" stroke="none" />
              <rect x="-5" y="-1" width="4" height="3" fill="#060402" stroke="none" />
              <path d="M1 -1c6-4 10 0 10 6" fill="none" strokeWidth="1.5" />
              <rect x="9" y="0" width="3" height="7" rx="0.8" stroke="none" />
            </g>
            <SegBar {...fuel} frac={fuelFrac(face.fuel_pct)} segs={FUEL_SEGS} warnLow={lowFuel} hotEnd={false} />
          </>
        )}
      </svg>

      <div className="bezel">
        <div className="bezel-left">
          <div className="round-pair" aria-hidden>
            <span className="round-btn minus">−</span>
            <span className="round-btn plus">+</span>
          </div>
          <div className="cancel">
            <svg className="dial" viewBox="0 0 20 16" width="16" height="13" aria-hidden>
              <circle cx="7" cy="8" r="6" fill="none" stroke="currentColor" strokeWidth="1.5" />
              <circle cx="7" cy="8" r="1.3" fill="currentColor" />
              <path d="M7 8 11 4" stroke="currentColor" strokeWidth="1.4" />
              <path d="M13 10 18 15M18 10 13 15" stroke="currentColor" strokeWidth="1.5" />
            </svg>
            PUSH CANCEL
          </div>
        </div>
        <TelltaleStrip lamps={face.lamps} battV={face.batt_v} />
        <div className="bezel-right">
          <span className="oval">{ap2 ? "CLOCK" : "SEL"}</span>
          <span className="oval">TRIP</span>
        </div>
      </div>
      <figcaption className="cluster-caption">
        {styleName} face · OEM cluster remains powered for the legal odometer · display-only overlay
      </figcaption>
    </figure>
  );
}
