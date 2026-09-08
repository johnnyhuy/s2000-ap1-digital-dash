import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DEFAULT_FACE_STYLE, FACE_STYLES, parseFaceStyle } from "./faceStyle.ts";

describe("face style", () => {
  it("defaults to ap1 and accepts ap2", () => {
    assert.equal(DEFAULT_FACE_STYLE, "ap1");
    assert.deepEqual([...FACE_STYLES], ["ap1", "ap2"]);
    assert.equal(parseFaceStyle(null), "ap1");
    assert.equal(parseFaceStyle("AP2"), "ap2");
    assert.equal(parseFaceStyle("nope"), "ap1");
  });
});
