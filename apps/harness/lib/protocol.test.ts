import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ProtocolError, telemetryToDict, validate } from "./protocol.ts";

describe("protocol", () => {
  it("accepts the frozen required fields", () => {
    const telem = validate({
      rpm: 6420.9,
      speed_kmh: 98,
      fuel_pct: 41,
      ect_c: 89,
      batt_v: 14.05,
      odo_km: 142857.3,
      lamps: { turn_l: 1, oil: 0 },
    });
    assert.equal(telem.rpm, 6420);
    assert.equal(telem.speed_kmh, 98);
    assert.equal(telem.lamps.turn_l, true);
    assert.equal(telem.lamps.oil, false);
  });

  it("clamps out-of-range fuel and rejects missing fields", () => {
    const telem = validate({
      rpm: 0,
      speed_kmh: 0,
      fuel_pct: 140,
      ect_c: 20,
      batt_v: 12,
      odo_km: 1,
    });
    assert.equal(telem.fuel_pct, 100);
    assert.throws(
      () => validate({ rpm: 1, speed_kmh: 1 }),
      (err: unknown) => err instanceof ProtocolError,
    );
  });

  it("round-trips to a Pi-shaped dict", () => {
    const dict = telemetryToDict(
      validate({
        rpm: 3000,
        speed_kmh: 80,
        fuel_pct: 48,
        ect_c: 88,
        batt_v: 14.1,
        odo_km: 10,
      }),
    );
    assert.deepEqual(Object.keys(dict).sort(), [
      "batt_v",
      "ect_c",
      "fuel_pct",
      "odo_km",
      "rpm",
      "speed_kmh",
    ]);
  });
});
