"use client";

import { useState } from "react";
import { DEFAULT_FACE_STYLE, type FaceStyle } from "@/lib/faceStyle";

const AP1_REFS = [
  {
    src: "/refs/flat/ap1_face.svg",
    alt: "AP1 OEM flat cluster lock (SVG)",
    caption: "refs/flat/ap1_face.svg — AP1 2.35:1 elevation lock",
  },
  {
    src: "/refs/flat/ap1_cluster_flat.png",
    alt: "AP1 OEM flat cluster lock (PNG)",
    caption: "refs/flat/ap1_cluster_flat.png — historical AP1 lock",
  },
] as const;

const AP2_REFS = [
  {
    src: "/refs/oem/ap2/ap2_s2ki_arched_gauges.jpg",
    alt: "AP2 OEM cluster with arched TEMP and FUEL gauges",
    caption: "refs/oem/ap2 — caution photo; UI is interpretive, not a plate",
  },
] as const;

function RefFigure({
  src,
  alt,
  caption,
}: {
  src: string;
  alt: string;
  caption: string;
}) {
  const [ok, setOk] = useState(true);
  if (!ok) return null;
  return (
    <figure className="ref-card">
      {/* Bundled copies of repo refs/; hide if the file was not copied. */}
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt={alt} onError={() => setOk(false)} />
      <figcaption>{caption}</figcaption>
    </figure>
  );
}

export function ReferencePanel({ style = DEFAULT_FACE_STYLE }: { style?: FaceStyle }) {
  const ap2 = style === "ap2";
  const refs = ap2 ? AP2_REFS : AP1_REFS;
  return (
    <aside className="ref-panel" aria-label="OEM reference images">
      <header>
        <h2>{ap2 ? "AP2 reference" : "AP1 OEM lock"}</h2>
        <p>
          {ap2
            ? "Arched TEMP / FUEL from refs/oem/ap2/. Not pixel-perfect — no measured plate."
            : "Straight TEMP / FUEL lock from refs/flat/. Historical AP1 path names stay."}
        </p>
      </header>
      <div className="ref-grid">
        {refs.map((ref) => (
          <RefFigure key={ref.src} {...ref} />
        ))}
      </div>
    </aside>
  );
}
