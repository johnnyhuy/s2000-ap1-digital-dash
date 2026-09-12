import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  AP2_TEMP_X_PCT,
  BAR_H_PCT,
  FACE,
  FUEL_X_PCT,
  MODULE_ASPECT,
  TEMP_SEGS,
  TEMP_W_PCT,
  TEMP_X_PCT,
  TEMP_Y_PCT,
  buildFaceGeom,
  faceGeom,
  tachBandPath,
  tachTickPath,
  tachArchXY,
  tachNumXY,
  TACH_BAND_OUTER,
  TACH_NUM_INSET,
  TACH_TICK_MAJOR,
} from "./geometry.ts";

function near(got: number, want: number, delta: number) {
  assert.ok(Math.abs(got - want) <= delta, `${got} !≈ ${want} ±${delta}`);
}

describe("face geometry", () => {
  it("locks the AP1 module aspect and straight bars", () => {
    assert.equal(FACE.style, "ap1");
    near(FACE.module.w / FACE.module.h, MODULE_ASPECT, 0.01);
    assert.equal(FACE.temp.y, FACE.fuel.y);
    assert.ok(FACE.temp.w > FACE.temp.h * 3);
    assert.ok(FACE.temp.x + FACE.temp.w < FACE.speed.x);
    assert.ok(FACE.fuel.x > FACE.speed.x);
    near(TEMP_X_PCT, 0.08, 0.0001);
    near(TEMP_Y_PCT, 0.505, 0.0001);
    near(TEMP_W_PCT, 0.16, 0.0001);
    near(FUEL_X_PCT, 0.76, 0.0001);
    near(BAR_H_PCT, 0.018, 0.0001);
    near(FACE.temp.x / FACE.module.w, TEMP_X_PCT, 0.01);
    near((FACE.temp.y - FACE.module.y) / FACE.module.h, TEMP_Y_PCT, 0.01);
  });

  it("stacks AP2 side gauges on the right without moving protocol", () => {
    const ap2 = buildFaceGeom("ap2");
    assert.equal(ap2.style, "ap2");
    assert.ok(ap2.temp.y < ap2.fuel.y);
    assert.ok(ap2.clock.y > ap2.speed.y);
    assert.ok(ap2.odo.y > ap2.clock.y);
    assert.ok(ap2.temp.x > ap2.speed.x);
    assert.ok(ap2.fuel.x > ap2.speed.x);
    near(ap2.temp.x / ap2.module.w, AP2_TEMP_X_PCT, 0.01);
    assert.notEqual(ap2.temp.y, faceGeom("ap1").temp.y);
  });

  it("drops tach numerals into the well, extra at 0 and 9", () => {
    const mid = tachNumXY(0.5);
    const arch = tachArchXY(0.5);
    assert.ok(mid.y > arch.y);
    assert.ok(Math.abs(mid.x - arch.x) < 6);
    assert.ok(TACH_NUM_INSET > TACH_BAND_OUTER);
    assert.ok(TACH_NUM_INSET > TACH_TICK_MAJOR.len + 16);
    const left = tachNumXY(0);
    const leftArch = tachArchXY(0);
    assert.ok(left.y > leftArch.y);
    assert.ok(left.y - leftArch.y > TACH_NUM_INSET * 0.4);
    const right = tachNumXY(1);
    const rightArch = tachArchXY(1);
    assert.ok(right.y > rightArch.y);
    assert.ok(left.y - leftArch.y > mid.y - arch.y);
    assert.ok(right.y - rightArch.y > mid.y - arch.y);
  });

  it("uses six thin AP1 temp ticks and slanted tach paths", () => {
    assert.equal(TEMP_SEGS, 6);
    const d = tachTickPath(0.05, 2, 16);
    assert.match(d, /^M /);
    assert.ok(d.includes("L "));
    const band = tachBandPath(0, 0.5, 1, 16);
    assert.match(band, /^M /);
    assert.ok(band.includes("Z"));
  });
});
