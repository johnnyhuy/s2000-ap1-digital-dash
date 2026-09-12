/**
 * Face geometry — AP1 lock from refs/flat/DIMENSIONS.md; AP2 is a
 * separate layout family (arched TEMP / FUEL on the right).
 * ViewBox is the module bounding box (1000 × 425.53 ≈ 2.35:1) plus a
 * short hardware strip under the cowl.
 */

import { DEFAULT_FACE_STYLE, type FaceStyle } from "./faceStyle.ts";

export const MODULE_ASPECT = 2.35;
export const VIEW_W = 1000;
export const MODULE_H = VIEW_W / MODULE_ASPECT;
export const VIEW_H = MODULE_H + 78;

export const STEP_W_PCT = 0.044;
export const NOTCH_TOP_PCT = 0.58;
export const NOTCH_BOT_PCT = 0.72;
export const ARCH_RISE_PCT = 0.28;
export const LAMP_Y_PCT = 0.805;
export const LCD_INSET_X_PCT = 0.01;
export const LCD_TOP_PCT = 0.055;
export const LCD_BOTTOM_PCT = 0.76;
export const TEMP_X_PCT = 0.08;
export const TEMP_Y_PCT = 0.505;
export const TEMP_W_PCT = 0.16;
export const FUEL_X_PCT = 0.76;
export const FUEL_Y_PCT = 0.505;
export const BAR_H_PCT = 0.018;
export const SPEED_X_PCT = 0.5;
export const SPEED_Y_PCT = 0.4;
export const ODO_Y_PCT = 0.5;
export const TACH_END_Y_PCT = 0.64;
export const TACH_PEAK_Y_PCT = 0.12;
export const TACH_INSET_X_PCT = 0.09;

/** AP2 interpretive side-gauge lock (not a measured plate). */
export const AP2_SPEED_X_PCT = 0.34;
export const AP2_ODO_Y_PCT = 0.52;
export const AP2_TEMP_X_PCT = 0.63;
export const AP2_TEMP_Y_PCT = 0.34;
export const AP2_FUEL_Y_PCT = 0.52;
export const AP2_SIDE_W_PCT = 0.3;
export const AP2_SIDE_H_PCT = 0.16;

export const TEMP_SEGS = 6;
export const FUEL_SEGS = 16;
export const AP2_TEMP_SEGS = 12;
export const AP2_FUEL_SEGS = 14;
export const REDLINE_BLOCKS = 5;
export const TACH_FILL_STEPS = 72;
export const TACH_MAJORS = 10;

export type FaceGeom = {
  style: FaceStyle;
  module: { x: number; y: number; w: number; h: number };
  step: number;
  springY: number;
  hoodPeakY: number;
  lcdPeakY: number;
  lcdSpringY: number;
  notchTopY: number;
  notchBotY: number;
  lcd: { x: number; y: number; w: number; h: number };
  temp: { x: number; y: number; w: number; h: number };
  fuel: { x: number; y: number; w: number; h: number };
  speed: { x: number; y: number };
  odo: { x: number; y: number };
  clock: { x: number; y: number };
  tachCx: number;
  tachCy: number;
  tachROuter: number;
  tachRInner: number;
  tachRNum: number;
  tachStart: number;
  tachSpan: number;
};

function archPoints(
  x0: number,
  x1: number,
  yPeak: number,
  ySpring: number,
  steps = 48,
): string {
  const rise = ySpring - yPeak;
  const pts: string[] = [];
  for (let i = 0; i <= steps; i += 1) {
    const t = i / steps;
    const u = 2 * t - 1;
    const x = x0 + (x1 - x0) * t;
    const y = yPeak + rise * u * u;
    pts.push(`${x.toFixed(2)},${y.toFixed(2)}`);
  }
  return pts.join(" ");
}

export function buildFaceGeom(style: FaceStyle = DEFAULT_FACE_STYLE): FaceGeom {
  const x = 0;
  const y = 0;
  const w = VIEW_W;
  const h = MODULE_H;
  const step = w * STEP_W_PCT;
  const inset = w * LCD_INSET_X_PCT;
  const lcdX = x + step + inset;
  const lcdW = w - 2 * step - 2 * inset;
  const lcdPeak = y + h * LCD_TOP_PCT;
  const lcdBottom = y + h * LCD_BOTTOM_PCT;
  const spring = y + h * ARCH_RISE_PCT;
  const barH = Math.max(11, h * BAR_H_PCT);
  const ap2 = style === "ap2";

  const speedXPct = ap2 ? AP2_SPEED_X_PCT : SPEED_X_PCT;
  const odoYPct = ap2 ? AP2_ODO_Y_PCT : ODO_Y_PCT;
  const cx = x + w * speedXPct;
  const endY = y + h * TACH_END_Y_PCT;
  const peakY = y + h * TACH_PEAK_Y_PCT;
  const endInset = lcdW * TACH_INSET_X_PCT;
  const x0 = lcdX + endInset;
  const x1 = lcdX + lcdW - endInset;
  const half = (x1 - x0) / 2;
  const drop = endY - peakY;
  const tachR = drop > 1 ? (half * half + drop * drop) / (2 * drop) : half;
  const tachCy = peakY + tachR;
  const startDeg = (Math.atan2(endY - tachCy, x0 - cx) * 180) / Math.PI;
  let endDeg = (Math.atan2(endY - tachCy, x1 - cx) * 180) / Math.PI;
  if (endDeg < startDeg) endDeg += 360;
  const span = endDeg - startDeg;

  const temp = ap2
    ? { x: x + w * AP2_TEMP_X_PCT, y: y + h * AP2_TEMP_Y_PCT, w: w * AP2_SIDE_W_PCT, h: h * AP2_SIDE_H_PCT }
    : { x: x + w * TEMP_X_PCT, y: y + h * TEMP_Y_PCT, w: w * TEMP_W_PCT, h: barH };
  const fuel = ap2
    ? { x: x + w * AP2_TEMP_X_PCT, y: y + h * AP2_FUEL_Y_PCT, w: w * AP2_SIDE_W_PCT, h: h * AP2_SIDE_H_PCT }
    : { x: x + w * FUEL_X_PCT, y: y + h * FUEL_Y_PCT, w: w * TEMP_W_PCT, h: barH };

  const speedY = y + h * SPEED_Y_PCT;
  const odoY = y + h * odoYPct;

  return {
    style,
    module: { x, y, w, h },
    step,
    springY: spring,
    hoodPeakY: y,
    lcdPeakY: lcdPeak,
    lcdSpringY: spring - h * 0.02,
    notchTopY: y + h * NOTCH_TOP_PCT,
    notchBotY: y + h * NOTCH_BOT_PCT,
    lcd: { x: lcdX, y: lcdPeak, w: lcdW, h: lcdBottom - lcdPeak },
    temp,
    fuel,
    speed: { x: cx, y: speedY },
    odo: { x: cx, y: ap2 ? speedY + 72 : odoY },
    clock: { x: cx, y: ap2 ? speedY + 36 : odoY },
    tachCx: cx,
    tachCy: tachCy,
    tachROuter: tachR,
    tachRInner: tachR - 28,
    tachRNum: tachR - 42,
    tachStart: (startDeg * Math.PI) / 180,
    tachSpan: (span * Math.PI) / 180,
  };
}

const GEOM: Record<FaceStyle, FaceGeom> = {
  ap1: buildFaceGeom("ap1"),
  ap2: buildFaceGeom("ap2"),
};

export function faceGeom(style: FaceStyle = DEFAULT_FACE_STYLE): FaceGeom {
  return GEOM[style];
}

/** Default AP1 lock — kept for existing call sites / tests. */
export const FACE = GEOM.ap1;

export function tachAngle(frac: number, geom: FaceGeom = FACE): number {
  const t = frac < 0 ? 0 : frac > 1 ? 1 : frac;
  return geom.tachStart + geom.tachSpan * t;
}

export function tachPoint(r: number, frac: number, geom: FaceGeom = FACE): { x: number; y: number } {
  const a = tachAngle(frac, geom);
  return {
    x: geom.tachCx + r * Math.cos(a),
    y: geom.tachCy + r * Math.sin(a),
  };
}

export function radialBlock(
  rIn: number,
  rOut: number,
  a0: number,
  a1: number,
  geom: FaceGeom = FACE,
): string {
  const { tachCx: cx, tachCy: cy } = geom;
  const p = (r: number, a: number) => `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`;
  return `M ${p(rIn, a0)} L ${p(rOut, a0)} L ${p(rOut, a1)} L ${p(rIn, a1)} Z`;
}

export function hoodPath(geom: FaceGeom = FACE): string {
  const { module: m, step, notchBotY, notchTopY, springY, hoodPeakY } = geom;
  const lx = m.x + step;
  const rx = m.x + m.w - step;
  const bot = m.y + m.h;
  const arch = archPoints(rx, lx, hoodPeakY, springY);
  return [
    `M ${m.x},${bot}`,
    `L ${m.x + m.w},${bot}`,
    `L ${m.x + m.w},${notchBotY}`,
    `L ${rx},${notchBotY}`,
    `L ${rx},${notchTopY}`,
    `L ${rx},${springY}`,
    `L ${arch}`,
    `L ${lx},${springY}`,
    `L ${lx},${notchTopY}`,
    `L ${lx},${notchBotY}`,
    `L ${m.x},${notchBotY}`,
    "Z",
  ].join(" ");
}

export function lcdPath(geom: FaceGeom = FACE): string {
  const { lcd, lcdSpringY, lcdPeakY } = geom;
  const rx = lcd.x + lcd.w;
  const bot = lcd.y + lcd.h;
  const arch = archPoints(rx, lcd.x, lcdPeakY, lcdSpringY);
  return [
    `M ${lcd.x},${bot}`,
    `L ${rx},${bot}`,
    `L ${rx},${lcdSpringY}`,
    `L ${arch}`,
    `L ${lcd.x},${lcdSpringY}`,
    "Z",
  ].join(" ");
}

export function archPoly(x0: number, x1: number, yPeak: number, ySpring: number): string {
  return archPoints(x0, x1, yPeak, ySpring);
}

export function tachArchXY(frac: number, geom: FaceGeom = FACE): { x: number; y: number } {
  const t = frac < 0 ? 0 : frac > 1 ? 1 : frac;
  const inset = geom.lcd.w * 0.055;
  const x0 = geom.lcd.x + inset;
  const x1 = geom.lcd.x + geom.lcd.w - inset;
  const u = 2 * t - 1;
  const rise = (geom.lcdSpringY - geom.lcdPeakY) * 0.92;
  return {
    x: x0 + (x1 - x0) * t,
    y: geom.lcdPeakY + 8 + rise * u * u,
  };
}

/** Inward offset from the printed band into the LCD well (viewBox units). */
export const TACH_NUM_INSET = 36;
export const TACH_BAND_OUTER = 16;
export const TACH_TICK_MAJOR = { w: 1.35, len: 11.5 };
export const TACH_TICK_MINOR = { w: 0.75, len: 6.8 };

export function tachNumXY(frac: number, geom: FaceGeom = FACE): { x: number; y: number } {
  const t = frac < 0 ? 0 : frac > 1 ? 1 : frac;
  const p = tachArchXY(t, geom);
  const n = tachArchNormal(t, geom);
  const end = Math.abs(2 * t - 1);
  const extra = 5.2 * end * end;
  return { x: p.x + n.x * TACH_NUM_INSET, y: p.y + n.y * TACH_NUM_INSET + extra };
}

export function tachArchNormal(frac: number, geom: FaceGeom = FACE): { x: number; y: number } {
  const t = frac < 0 ? 0 : frac > 1 ? 1 : frac;
  const inset = geom.lcd.w * 0.055;
  const spanX = geom.lcd.w - 2 * inset;
  const rise = (geom.lcdSpringY - geom.lcdPeakY) * 0.92;
  const u = 2 * t - 1;
  const dx = spanX;
  const dy = 4 * rise * u;
  const n = Math.hypot(dx, dy) || 1;
  let nx = dy / n;
  let ny = -dx / n;
  if (ny < 0) {
    nx = -nx;
    ny = -ny;
  }
  return { x: nx, y: ny };
}

export function tachTickPath(
  frac: number,
  width: number,
  length: number,
  geom: FaceGeom = FACE,
  inset = 1.2,
): string {
  const p = tachArchXY(frac, geom);
  const nrm = tachArchNormal(frac, geom);
  const tx = -nrm.y;
  const ty = nrm.x;
  const hw = width * 0.5;
  const x0 = p.x + nrm.x * inset;
  const y0 = p.y + nrm.y * inset;
  const pts = [
    [x0 - tx * hw, y0 - ty * hw],
    [x0 + tx * hw, y0 + ty * hw],
    [x0 + tx * hw + nrm.x * length, y0 + ty * hw + nrm.y * length],
    [x0 - tx * hw + nrm.x * length, y0 - ty * hw + nrm.y * length],
  ];
  return `M ${pts.map(([x, y]) => `${x.toFixed(2)} ${y.toFixed(2)}`).join(" L ")} Z`;
}

export function tachBandPath(
  frac0: number,
  frac1: number,
  inner: number,
  outer: number,
  geom: FaceGeom = FACE,
  steps = 48,
): string {
  const t0 = frac0 < 0 ? 0 : frac0 > 1 ? 1 : frac0;
  const t1 = frac1 < 0 ? 0 : frac1 > 1 ? 1 : frac1;
  if (t1 <= t0 + 1e-4) return "";
  const n = Math.max(8, Math.round(steps * (t1 - t0)));
  const outerPts: string[] = [];
  const innerPts: string[] = [];
  for (let i = 0; i <= n; i += 1) {
    const f = t0 + (t1 - t0) * (i / n);
    const p = tachArchXY(f, geom);
    const nrm = tachArchNormal(f, geom);
    outerPts.push(`${(p.x + nrm.x * inner).toFixed(2)},${(p.y + nrm.y * inner).toFixed(2)}`);
    innerPts.push(`${(p.x + nrm.x * outer).toFixed(2)},${(p.y + nrm.y * outer).toFixed(2)}`);
  }
  innerPts.reverse();
  return `M ${outerPts.join(" L ")} L ${innerPts.join(" L ")} Z`;
}

/** Shallow rainbow (concave-down) along a side-gauge box — AP2 only. */
export function sideArchPoint(
  box: { x: number; y: number; w: number; h: number },
  frac: number,
): { x: number; y: number } {
  const t = frac < 0 ? 0 : frac > 1 ? 1 : frac;
  const u = 2 * t - 1;
  return {
    x: box.x + box.w * t,
    y: box.y + box.h * 0.22 + box.h * 0.72 * u * u,
  };
}
