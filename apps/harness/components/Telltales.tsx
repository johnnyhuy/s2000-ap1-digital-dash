import type { LampMap } from "@/lib/protocol";
import { BATT_LOW_V } from "@/lib/protocol";
import { PICTOGRAMS } from "./LampIcons";

type Tone = "red" | "amber" | "green" | "blue";

type LampSpec = {
  kind: keyof typeof PICTOGRAMS | "abs" | "brake" | "maint" | "eps" | "srs";
  key: string;
  tone: Tone;
  label: string;
  width: number;
  word?: string | [string, string];
};

export const LAMP_STRIP: LampSpec[] = [
  { kind: "turn_l", key: "turn_l", tone: "green", label: "Left turn", width: 20 },
  { kind: "high_beam", key: "high_beam", tone: "blue", label: "High beam", width: 28 },
  { kind: "abs", key: "abs", tone: "amber", label: "ABS", width: 34, word: "ABS" },
  { kind: "brake", key: "brake", tone: "red", label: "BRAKE", width: 50, word: "BRAKE" },
  { kind: "battery", key: "batt_warn", tone: "red", label: "Battery", width: 22 },
  { kind: "oil", key: "oil", tone: "red", label: "Oil", width: 26 },
  { kind: "cel", key: "cel", tone: "amber", label: "Check engine", width: 28 },
  { kind: "immobilizer", key: "immobilizer", tone: "green", label: "Immobilizer", width: 24 },
  { kind: "maint", key: "maint", tone: "amber", label: "MAINT REQ'D", width: 38, word: ["MAINT", "REQ'D"] },
  { kind: "eps", key: "eps", tone: "amber", label: "EPS", width: 28, word: "EPS" },
  { kind: "seatbelt", key: "seatbelt", tone: "red", label: "Seatbelt", width: 20 },
  { kind: "door", key: "door", tone: "red", label: "Door", width: 22 },
  { kind: "srs", key: "srs", tone: "red", label: "SRS", width: 24, word: "SRS" },
  { kind: "turn_r", key: "turn_r", tone: "green", label: "Right turn", width: 20 },
];

const TONE: Record<Tone, string> = {
  red: "#e22820",
  amber: "#ec941c",
  green: "#22b84c",
  blue: "#1c54d8",
};

const GHOST = "#1a1816";

export function TelltaleStrip({
  lamps,
  battV,
  bulbCheck = false,
}: {
  lamps: LampMap;
  battV: number;
  bulbCheck?: boolean;
}) {
  return (
    <div className="lamp-strip" role="group" aria-label="OEM telltales">
      {LAMP_STRIP.map((spec, i) => {
        const extra = spec.key === "batt_warn" && battV < BATT_LOW_V;
        const lit = bulbCheck || Boolean(lamps[spec.key] || extra);
        const color = lit ? TONE[spec.tone] : GHOST;
        const word = spec.word;
        const Pictogram = spec.kind in PICTOGRAMS ? PICTOGRAMS[spec.kind as keyof typeof PICTOGRAMS] : null;
        return (
          <span
            key={spec.kind}
            className={`telltale telltale-${spec.tone}${lit ? " telltale-on" : ""}`}
            title={spec.label}
            style={{ color, ["--lamp" as string]: color, ["--i" as string]: i }}
          >
            {word ? (
              <span className="telltale-word">
                {Array.isArray(word)
                  ? word.map((line) => (
                      <span key={line} className="telltale-word-line">
                        {line}
                      </span>
                    ))
                  : word}
              </span>
            ) : Pictogram ? (
              <Pictogram className="telltale-icon" width={spec.width} />
            ) : null}
            <span className="sr-only">
              {spec.label}
              {lit ? " on" : " off"}
            </span>
          </span>
        );
      })}
    </div>
  );
}

export function HardwareBezel({
  lamps,
  battV,
  selLabel,
  bulbCheck = false,
}: {
  lamps: LampMap;
  battV: number;
  selLabel: string;
  bulbCheck?: boolean;
}) {
  return (
    <div className="bezel" aria-hidden={false}>
      <div className="bezel-left">
        <div className="round-pair">
          <span className="round-btn minus">−</span>
          <span className="round-btn">+</span>
        </div>
        <p className="cancel">
          <svg className="cancel-mark" viewBox="0 0 28 16" aria-hidden>
            <circle cx="8" cy="8" r="6.1" fill="none" stroke="currentColor" strokeWidth="1.55" />
            <circle cx="8" cy="8" r="1.25" fill="currentColor" />
            <line x1="8" y1="8" x2="12.1" y2="4.3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
            <line x1="3.4" y1="5.1" x2="2.1" y2="3.6" stroke="currentColor" strokeWidth="1.35" />
            <line x1="4.6" y1="3.6" x2="3.6" y2="2.1" stroke="currentColor" strokeWidth="1.35" />
            <line x1="6.4" y1="2.8" x2="5.8" y2="1.15" stroke="currentColor" strokeWidth="1.35" />
            <line x1="8.4" y1="2.4" x2="8.4" y2="0.7" stroke="currentColor" strokeWidth="1.35" />
            <path d="M18.4 4.2 25.2 11.1M25.2 4.2 18.4 11.1" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
          </svg>
          PUSH CANCEL
        </p>
      </div>
      <TelltaleStrip lamps={lamps} battV={battV} bulbCheck={bulbCheck} />
      <div className="bezel-right">
        <span className="oval">{selLabel}</span>
        <span className="oval">TRIP</span>
      </div>
    </div>
  );
}
