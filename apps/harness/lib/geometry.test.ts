import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  AP2_TEMP_X_PCT,
  FACE,
  MODULE_ASPECT,
  TEMP_SEGS,
  TEMP_X_PCT,
  buildFaceGeom,
  faceGeom,
  tachTickPath,
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
    near(FACE.temp.x / FACE.module.w, TEMP_X_PCT, 0.01);
  });

  it("stacks AP2 side gauges on the right without moving protocol", () => {
    const ap2 = buildFaceGeom("ap2");
    assert.equal(ap2.style, "ap2");
    assert.ok(ap2.temp.y < ap2.fuel.y);
    assert.ok(ap2.temp.x > ap2.speed.x);
    assert.ok(ap2.fuel.x > ap2.speed.x);
    near(ap2.temp.x / ap2.module.w, AP2_TEMP_X_PCT, 0.01);
    assert.notEqual(ap2.temp.y, faceGeom("ap1").temp.y);
  });

  it("uses six thin AP1 temp ticks and slanted tach paths", () => {
    assert.equal(TEMP_SEGS, 6);
    const d = tachTickPath(0.05, 2, 16);
    assert.match(d, /^M /);
    assert.ok(d.includes("L "));
  });
});
