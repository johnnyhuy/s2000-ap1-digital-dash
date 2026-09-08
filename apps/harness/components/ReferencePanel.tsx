"use client";

import { useState } from "react";

const REFS = [
  {
    src: "/refs/flat/ap1_face.svg",
    alt: "AP1 OEM flat cluster lock (SVG)",
    caption: "refs/flat/ap1_face.svg — 2.35:1 elevation lock",
  },
  {
    src: "/refs/flat/ap1_cluster_flat.png",
    alt: "AP1 OEM flat cluster lock (PNG)",
    caption: "refs/flat/ap1_cluster_flat.png",
  },
] as const;

function RefFigure({ src, alt, caption }: (typeof REFS)[number]) {
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

export function ReferencePanel() {
  return (
    <aside className="ref-panel" aria-label="OEM reference images">
      <header>
        <h2>OEM lock</h2>
        <p>
          Side-by-side copies from <code>refs/flat/</code> on main. Missing files
          hide themselves — pixel-perfect pygame parity is a separate track.
        </p>
      </header>
      <div className="ref-grid">
        {REFS.map((ref) => (
          <RefFigure key={ref.src} {...ref} />
        ))}
      </div>
    </aside>
  );
}
