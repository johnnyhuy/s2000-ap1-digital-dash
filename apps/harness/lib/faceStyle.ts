/**
 * Cluster face style — layout only; protocol JSON fields stay frozen.
 *
 * ap1 (default): locked flat elevation — straight TEMP / FUEL.
 * ap2: interpretive arched side-gauges from refs/oem/ap2/ (not pixel-perfect).
 */

export const FACE_STYLES = ["ap1", "ap2"] as const;
export type FaceStyle = (typeof FACE_STYLES)[number];
export const DEFAULT_FACE_STYLE: FaceStyle = "ap1";

export const FACE_STYLE_LABELS: Record<FaceStyle, string> = {
  ap1: "AP1",
  ap2: "AP2",
};

export const FACE_STYLE_HINTS: Record<FaceStyle, string> = {
  ap1: "Straight TEMP / FUEL — locked flat elevation",
  ap2: "Arched side gauges — interpretive, not a measured plate",
};

export function parseFaceStyle(value: string | null | undefined): FaceStyle {
  const token = (value ?? "").trim().toLowerCase();
  if (token === "ap2") return "ap2";
  return "ap1";
}
