/**
 * Flat AP1 face lock — percentages from refs/flat/DIMENSIONS.md.
 * ViewBox is the module bounding box (1000 × 425.53 ≈ 2.35:1) plus a
 * short hardware strip under the cowl.
 */

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
export const TEMP_X_PCT = 0.075;
export const TEMP_Y_PCT = 0.72;
export const TEMP_W_PCT = 0.18;
export const FUEL_X_PCT = 0.745;
export const FUEL_Y_PCT = 0.72;
export const BAR_H_PCT = 0.03;
export const SPEED_X_PCT = 0.5;
export const SPEED_Y_PCT = 0.4;
export const ODO_Y_PCT = 0.5;
export const TACH_END_Y_PCT = 0.64;
export const TACH_PEAK_Y_PCT = 0.12;
export const TACH_INSET_X_PCT = 0.09;

export const TEMP_SEGS = 14;
export const FUEL_SEGS = 16;
export const REDLINE_BLOCKS = 5;
export const TACH_FILL_STEPS = 72;
export const TACH_MAJORS = 10;

export type FaceGeom = {
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

export function buildFaceGeom(): FaceGeom {
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
  const barH = Math.max(10, h * BAR_H_PCT);

  const cx = x + w * SPEED_X_PCT;
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

  return {
    module: { x, y, w, h },
    step,
    springY: spring,
    hoodPeakY: y,
    lcdPeakY: lcdPeak,
    lcdSpringY: spring - h * 0.02,
    notchTopY: y + h * NOTCH_TOP_PCT,
    notchBotY: y + h * NOTCH_BOT_PCT,
    lcd: { x: lcdX, y: lcdPeak, w: lcdW, h: lcdBottom - lcdPeak },
    temp: { x: x + w * TEMP_X_PCT, y: y + h * TEMP_Y_PCT, w: w * TEMP_W_PCT, h: barH },
    fuel: { x: x + w * FUEL_X_PCT, y: y + h * FUEL_Y_PCT, w: w * TEMP_W_PCT, h: barH },
    speed: { x: cx, y: y + h * SPEED_Y_PCT },
    odo: { x: cx, y: y + h * ODO_Y_PCT },
    tachCx: cx,
    tachCy: tachCy,
    tachROuter: tachR,
    tachRInner: tachR - 28,
    tachRNum: tachR - 42,
    tachStart: (startDeg * Math.PI) / 180,
    tachSpan: (span * Math.PI) / 180,
  };
}

export const FACE = buildFaceGeom();

export function tachAngle(frac: number): number {
  const t = frac < 0 ? 0 : frac > 1 ? 1 : frac;
  return FACE.tachStart + FACE.tachSpan * t;
}

export function tachPoint(r: number, frac: number): { x: number; y: number } {
  const a = tachAngle(frac);
  return {
    x: FACE.tachCx + r * Math.cos(a),
    y: FACE.tachCy + r * Math.sin(a),
  };
}

export function radialBlock(
  rIn: number,
  rOut: number,
  a0: number,
  a1: number,
): string {
  const { tachCx: cx, tachCy: cy } = FACE;
  const p = (r: number, a: number) => `${cx + r * Math.cos(a)},${cy + r * Math.sin(a)}`;
  return `M ${p(rIn, a0)} L ${p(rOut, a0)} L ${p(rOut, a1)} L ${p(rIn, a1)} Z`;
}

export function hoodPath(): string {
  const { module: m, step, notchBotY, notchTopY, springY, hoodPeakY } = FACE;
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

export function lcdPath(): string {
  const { lcd, lcdSpringY, lcdPeakY } = FACE;
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
