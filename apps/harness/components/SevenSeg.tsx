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
  const t = Math.max(2.0, h * 0.118);
  const tg = t * 1.08;
  const gap = Math.max(1.3, t * 0.38);
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
  digitH = 42,
  color = "#e02018",
  ghostColor = "#3a0c0a",
  x = 0,
  y = 0,
  italic = 0.08,
}: {
  text: string;
  ghost?: string;
  digitH?: number;
  color?: string;
  ghostColor?: string;
  x?: number;
  y?: number;
  italic?: number;
}) {
  const dw = Math.max(8, digitH * 0.62);
  const gap = Math.max(2, dw / 6);
  const chars = text.split("");
  const gchars = ghost.padEnd(chars.length, "8").slice(0, chars.length).split("");
  const xs = chars.reduce<number[]>((acc) => {
    const prev = acc.length === 0 ? 0 : acc[acc.length - 1] + (chars[acc.length - 1] === "." ? dw / 5 : dw + gap);
    acc.push(prev);
    return acc;
  }, []);
  const nodes = chars.map((ch, i) => {
    if (ch === ".") {
      return (
        <circle
          key={`d${i}`}
          cx={xs[i] + 3}
          cy={digitH - 3}
          r={Math.max(2.2, digitH / 11)}
          fill={color}
          className="seg-lit seg-red"
        />
      );
    }
    const paths = digitPaths(dw, digitH);
    const lit = new Set((DIGITS[ch] ?? "").split(""));
    const ghostLit = new Set((DIGITS[gchars[i]] ?? "abcdefg").split(""));
    return (
      <g key={`g${i}`} transform={`translate(${xs[i]} 0)`}>
        {Object.entries(paths).map(([name, d]) => (
          <path key={name} d={d} fill={ghostLit.has(name) ? ghostColor : "none"} />
        ))}
        {Object.entries(paths).map(([name, d]) =>
          lit.has(name) ? (
            <path key={`l${name}`} d={d} fill={color} className="seg-lit seg-red" />
          ) : null,
        )}
      </g>
    );
  });
  const skew = (-italic * 55).toFixed(2);
  return (
    <g transform={`translate(${x} ${y}) skewX(${skew})`} className="seven-seg" aria-hidden>
      {nodes}
    </g>
  );
}
