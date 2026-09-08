import {
  FACE,
  FUEL_SEGS,
  REDLINE_BLOCKS,
  TACH_FILL_STEPS,
  TACH_MAJORS,
  TEMP_SEGS,
  VIEW_H,
  VIEW_W,
  archPoly,
  hoodPath,
  lcdPath,
  radialBlock,
  tachAngle,
  tachPoint,
} from "@/lib/geometry";
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

function TachSegments({ litFrac }: { litFrac: number }) {
  const redFrom = 8 / 9;
  const wash = [];
  for (let i = 0; i < 36; i += 1) {
    const t0 = i / 36;
    const t1 = (i + 1) / 36;
    const pad = 0.02;
    wash.push(
      <path
        key={`w${i}`}
        d={radialBlock(
          FACE.tachRInner + 4,
          FACE.tachROuter - 2,
          tachAngle(t0 + (t1 - t0) * pad),
          tachAngle(t1 - (t1 - t0) * pad),
        )}
        fill={AMBER_WASH}
      />,
    );
  }

  const segs = [];
  for (let i = 0; i < TACH_FILL_STEPS; i += 1) {
    const t0 = i / TACH_FILL_STEPS;
    const t1 = (i + 1) / TACH_FILL_STEPS;
    const mid = (t0 + t1) * 0.5;
    if (mid >= redFrom) continue;
    const on = mid <= litFrac + 1e-6;
    const pad = 0.1;
    segs.push(
      <path
        key={`s${i}`}
        className={on ? "seg-lit" : undefined}
        d={radialBlock(
          FACE.tachRInner + 6,
          FACE.tachROuter - 3,
          tachAngle(t0 + (t1 - t0) * pad),
          tachAngle(t1 - (t1 - t0) * pad),
        )}
        fill={on ? lerpHex(AMBER, AMBER_HOT, mid) : AMBER_GHOST}
      />,
    );
  }

  const reds = [];
  for (let i = 0; i < REDLINE_BLOCKS; i += 1) {
    const t0 = redFrom + (1 - redFrom) * (i / REDLINE_BLOCKS);
    const t1 = redFrom + (1 - redFrom) * ((i + 1) / REDLINE_BLOCKS);
    const mid = (t0 + t1) * 0.5;
    const on = mid <= litFrac + 1e-6;
    const pad = 0.08;
    reds.push(
      <path
        key={`r${i}`}
        className={on ? "seg-lit" : undefined}
        d={radialBlock(
          FACE.tachRInner - 3,
          FACE.tachROuter + 4,
          tachAngle(t0 + (t1 - t0) * pad),
          tachAngle(t1 - (t1 - t0) * pad),
        )}
        fill={on ? RED : RED_GHOST}
      />,
    );
  }

  const ticks = [];
  for (let i = 0; i < TACH_MAJORS; i += 1) {
    const frac = i / 9;
    if (frac >= redFrom - 1e-6) continue;
    const a = tachAngle(frac);
    const half = (0.55 * Math.PI) / 180;
    ticks.push(
      <path
        key={`t${i}`}
        d={radialBlock(FACE.tachRInner - 1, FACE.tachROuter + 2, a - half, a + half)}
        fill={WHITE}
      />,
    );
    if (i < 8) {
      const am = tachAngle((i + 0.5) / 9);
      const hm = (0.32 * Math.PI) / 180;
      ticks.push(
        <path
          key={`m${i}`}
          d={radialBlock(FACE.tachRInner + 8, FACE.tachROuter - 4, am - hm, am + hm)}
          fill="#a8a094"
        />,
      );
    }
  }

  return (
    <g aria-hidden>
      {wash}
      {segs}
      {reds}
      {ticks}
    </g>
  );
}

function TachNumbers() {
  return (
    <g className="tach-nums">
      {Array.from({ length: 10 }, (_, i) => {
        const hot = i >= 8;
        let { x, y } = tachPoint(FACE.tachRNum, i / 9);
        if (i === 0) {
          x += 12;
          y -= 16;
        } else if (i === 1) {
          x += 4;
          y -= 8;
        } else if (i >= 8) {
          x -= 6;
          y -= 12;
        }
        const lean = (i / 9 - 0.5) * 36;
        return (
          <text
            key={i}
            x={x}
            y={y}
            fill={hot ? RED : AMBER}
            textAnchor="middle"
            dominantBaseline="middle"
            transform={`rotate(${lean} ${x} ${y})`}
          >
            {i}
          </text>
        );
      })}
      {(() => {
        const p = tachPoint(FACE.tachRInner - 4, 0.04);
        return (
          <text x={p.x - 8} y={p.y + 22} fill={DIM} textAnchor="middle" className="micro">
            x1000r/min
          </text>
        );
      })()}
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
  const gap = 1.4;
  const segW = (w - gap * (segs - 1)) / segs;
  const lit = Math.round(frac * segs);
  return (
    <g>
      <line x1={x} y1={y + h + 1.5} x2={x + w} y2={y + h + 1.5} stroke="#4e3210" strokeWidth="1.4" />
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
            x={x + i * (segW + gap)}
            y={y}
            width={Math.max(2.4, segW)}
            height={h}
            rx={0.8}
            fill={fill}
            className={on ? "seg-lit" : undefined}
          />
        );
      })}
    </g>
  );
}

export function ClusterFace({ face }: { face: DisplayState }) {
  const litFrac = Math.max(0, Math.min(1, face.rpm / RPM_REDLINE));
  const hot = face.ect_c >= ECT_HOT_C;
  const lowFuel = face.fuel_pct < FUEL_LOW_PCT;
  const battWarn = face.batt_v < BATT_LOW_V || Boolean(face.lamps.batt_warn);
  const speed = Math.round(Math.max(0, Math.min(399, face.speed_kmh)));
  const { temp, fuel, speed: sc, odo, module: m, step, hoodPeakY, springY } = FACE;
  const lip = archPoly(m.x + step, m.x + m.w - step, hoodPeakY + 3, springY - 2);

  return (
    <figure className="cluster">
      <svg
        viewBox={`-8 -6 ${VIEW_W + 16} ${VIEW_H}`}
        role="img"
        aria-label={`AP1 cluster, ${speed} kilometres per hour, ${Math.round(face.rpm)} rpm`}
      >
        <defs>
          <filter id="amber-bloom" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path d={hoodPath()} fill="#1a1918" stroke="#3a342c" strokeWidth="1.6" />
        <polyline points={lip} fill="none" stroke="#2c2824" strokeWidth="2.2" />
        <path d={lcdPath()} fill="#060402" stroke="#16120e" strokeWidth="1.2" />
        <TachSegments litFrac={litFrac} />
        <TachNumbers />

        <g className="readout" filter="url(#amber-bloom)">
          <text x={sc.x} y={sc.y} textAnchor="middle" dominantBaseline="middle" className="speed">
            {speed}
          </text>
        </g>
        <text x={sc.x + 86} y={sc.y - 8} className="unit" fill={AMBER}>
          km/h
        </text>
        <text x={sc.x + 86} y={sc.y + 12} className="mph" fill={DIM}>
          mph
        </text>
        <text x={odo.x} y={odo.y} textAnchor="middle" className="odo" fill={AMBER} filter="url(#amber-bloom)">
          {`ODO  ${face.odo_km.toFixed(1).padStart(8, "0")}    TRIP  ${face.trip_km.toFixed(1).padStart(5, "0")}`}
        </text>
        <text x={odo.x + 248} y={odo.y} className="batt" fill={battWarn ? RED : DIM}>
          {`${face.batt_v.toFixed(1)}V`}
        </text>

        <text x={temp.x - 12} y={temp.y + temp.h * 0.85} className="tiny" fill={AMBER} textAnchor="middle">
          C
        </text>
        <text x={temp.x + temp.w + 12} y={temp.y + temp.h * 0.85} className="tiny" fill={hot ? RED : AMBER} textAnchor="middle">
          H
        </text>
        <g transform={`translate(${temp.x + 8} ${temp.y - 16})`} fill={hot ? RED : AMBER}>
          <rect x="-2" y="-8" width="4" height="11" rx="2" />
          <circle cx="0" cy="6" r="4" />
        </g>
        <SegBar {...temp} frac={ectFrac(face.ect_c)} segs={TEMP_SEGS} warnLow={false} hotEnd={hot} />

        <text x={fuel.x - 12} y={fuel.y + fuel.h * 0.85} className="tiny" fill={lowFuel ? RED : AMBER} textAnchor="middle">
          E
        </text>
        <text x={fuel.x + fuel.w + 12} y={fuel.y + fuel.h * 0.85} className="tiny" fill={AMBER} textAnchor="middle">
          F
        </text>
        <g
          transform={`translate(${fuel.x + fuel.w - 6} ${fuel.y - 14})`}
          fill={lowFuel ? "#e68424" : AMBER}
          stroke={lowFuel ? "#e68424" : AMBER}
        >
          <rect x="-7" y="-4" width="8" height="11" rx="1.2" />
          <rect x="-5" y="-8" width="5" height="4" rx="0.6" />
          <path d="M1 -2 7 -6v10" fill="none" strokeWidth="1.4" />
        </g>
        <SegBar {...fuel} frac={fuelFrac(face.fuel_pct)} segs={FUEL_SEGS} warnLow={lowFuel} hotEnd={false} />
      </svg>

      <div className="bezel">
        <div className="bezel-left">
          <div className="rocker" aria-hidden>
            <span className="minus">−</span>
            <span className="plus">+</span>
          </div>
          <div className="cancel">
            <span className="dial" />
            PUSH CANCEL
          </div>
        </div>
        <TelltaleStrip lamps={face.lamps} battV={face.batt_v} />
        <div className="bezel-right">
          <span className="oval">SEL</span>
          <span className="oval">TRIP</span>
        </div>
      </div>
      <figcaption className="cluster-caption">
        OEM cluster remains powered for the legal odometer · display-only overlay
      </figcaption>
    </figure>
  );
}
