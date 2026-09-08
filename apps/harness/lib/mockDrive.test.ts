import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { REQUIRED_FIELDS } from "./protocol.ts";
import { SCENARIOS, frameAt } from "./mockDrive.ts";

describe("mock drive", () => {
  for (const scenario of SCENARIOS) {
    it(`emits frozen fields for ${scenario}`, () => {
      const frame = frameAt(1.25, 142_857.3, scenario);
      for (const key of REQUIRED_FIELDS) {
        assert.equal(typeof frame[key], "number");
      }
      assert.equal(typeof frame.lamps, "object");
    });
  }

  it("warn lights the OEM extras", () => {
    const frame = frameAt(0, 0, "warn");
    assert.equal(frame.fuel_pct, 8);
    assert.equal(frame.ect_c, 108);
    assert.equal(frame.lamps.cel, true);
    assert.equal(frame.lamps.brake, true);
  });
});
