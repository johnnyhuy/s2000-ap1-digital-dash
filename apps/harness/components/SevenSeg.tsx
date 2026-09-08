/** Soft OEM-style 7-seg (rounded hex segments + ghost). Display only. */

const DIGITS: Record<string, string> = {
  "0": "abcdef",
  "1": "bc",
  "2": "abged",
  "3": "abcdg",
  "4": "bcfg",
  "5": "acdfg",
  "6": "acdefg",
  "7": "abc",
  "8": "abcdefg",
  "9": "abcdfg",
  " ": "",
  "-": "g",
};

function hSeg(x: number, y: number, w: number, t: number): string {
  const n = t * 0.78;
  return `M ${x + n} ${y} L ${x + w - n} ${y} L ${x + w} ${y + t / 2} L ${x + w - n} ${y + t} L ${x + n} ${y + t} L ${x} ${y + t / 2} Z`;
}

function vSeg(x: number, y: number, h: number, t: number): string {
  const n = t * 0.78;
  return `M ${x + t / 2} ${y} L ${x + t} ${y + n} L ${x + t} ${y + h - n} L ${x + t / 2} ${y + h} L ${x} ${y + h - n} L ${x} ${y + n} Z`;
}

function digitPaths(w: number, h: number): Record<string, string> {
  const t = Math.max(2.2, h * 0.145);
  const tg = t * 1.16;
  const gap = Math.max(1.1, t * 0.28);
  const inner = w - t;
  const half = (h - t) / 2;
  const ax = t * 0.35;
  return {
    a: hSeg(ax, 0, inner, t),
    g: hSeg(ax - t * 0.04, half - (tg - t) / 2, inner + t * 0.08, tg),
    d: hSeg(ax, h - t, inner, t),
    f: vSeg(0, t * 0.55, half - gap, t),
    b: vSeg(w - t, t * 0.55, half - gap, t),
    e: vSeg(0, half + t * 0.35, half - gap, t),
    c: vSeg(w - t, half + t * 0.35, half - gap, t),
  };
}

export function SevenSeg({
  text,
  ghost = "188",
  digitH = 72,
  color = "#ffb02e",
  ghostColor = "#281a0a",
}: {
  text: string;
  ghost?: string;
  digitH?: number;
  color?: string;
  ghostColor?: string;
}) {
  const dw = Math.max(8, digitH * 0.62);
  const gap = Math.max(2, dw / 6);
  const chars = text.split("");
  const gchars = ghost.padEnd(chars.length, "8").slice(0, chars.length).split("");
  let x = 0;
  const nodes = chars.map((ch, i) => {
    if (ch === ".") {
      const cx = x + 3;
      x += dw / 5;
      return <circle key={`d${i}`} cx={cx} cy={digitH - 4} r={Math.max(1.6, digitH / 14)} fill={color} />;
    }
    const paths = digitPaths(dw, digitH);
    const lit = new Set((DIGITS[ch] ?? "").split(""));
    const ghostLit = new Set((DIGITS[gchars[i]] ?? "abcdefg").split(""));
    const ox = x;
    x += dw + gap;
    return (
      <g key={`g${i}`} transform={`translate(${ox} 0)`}>
        {Object.entries(paths).map(([name, d]) => (
          <path key={name} d={d} fill={ghostLit.has(name) ? ghostColor : "none"} />
        ))}
        {Object.entries(paths).map(([name, d]) =>
          lit.has(name) ? <path key={`l${name}`} d={d} fill={color} className="seg-lit" /> : null,
        )}
      </g>
    );
  });
  return (
    <svg width={x} height={digitH} viewBox={`0 0 ${x} ${digitH}`} aria-hidden overflow="visible">
      {nodes}
    </svg>
  );
}
