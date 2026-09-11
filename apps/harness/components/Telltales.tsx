import type { LampMap } from "@/lib/protocol";
import { BATT_LOW_V } from "@/lib/protocol";

type Tone = "red" | "amber" | "green" | "blue";

type LampSpec = {
  kind: string;
  key: string;
  tone: Tone;
  label: string;
  width: number;
  word?: string | [string, string];
};

export const LAMP_STRIP: LampSpec[] = [
  { kind: "turn_l", key: "turn_l", tone: "green", label: "Left turn", width: 16 },
  { kind: "high_beam", key: "high_beam", tone: "blue", label: "High beam", width: 18 },
  { kind: "abs", key: "abs", tone: "amber", label: "ABS", width: 22, word: "ABS" },
  { kind: "brake", key: "brake", tone: "red", label: "BRAKE", width: 32, word: "BRAKE" },
  { kind: "battery", key: "batt_warn", tone: "red", label: "Battery", width: 16 },
  { kind: "oil", key: "oil", tone: "red", label: "Oil", width: 18 },
  { kind: "cel", key: "cel", tone: "amber", label: "Check engine", width: 20 },
  { kind: "immobilizer", key: "immobilizer", tone: "green", label: "Immobilizer", width: 16 },
  { kind: "maint", key: "maint", tone: "amber", label: "MAINT REQ'D", width: 24, word: ["MAINT", "REQ'D"] },
  { kind: "eps", key: "eps", tone: "amber", label: "EPS", width: 20, word: "EPS" },
  { kind: "seatbelt", key: "seatbelt", tone: "red", label: "Seatbelt", width: 15 },
  { kind: "door", key: "door", tone: "red", label: "Door", width: 18 },
  { kind: "srs", key: "srs", tone: "red", label: "SRS", width: 16, word: "SRS" },
  { kind: "turn_r", key: "turn_r", tone: "green", label: "Right turn", width: 16 },
];

const TONE: Record<Tone, string> = {
  red: "#d6221e",
  amber: "#e48a1a",
  green: "#2cc458",
  blue: "#1c56d6",
};

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
      {LAMP_STRIP.map((spec) => {
        const extra = spec.key === "batt_warn" && battV < BATT_LOW_V;
        const lit = bulbCheck || Boolean(lamps[spec.key] || extra);
        const color = lit ? TONE[spec.tone] : undefined;
        const src = `/icons/${spec.kind}.svg`;
        const word = spec.word;
        return (
          <span
            key={spec.kind}
            className={`telltale${lit ? " telltale-on" : ""}`}
            title={spec.label}
            style={color ? { color, ["--lamp" as string]: color } : undefined}
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
            ) : (
              <span
                className="telltale-icon"
                style={{
                  width: spec.width,
                  WebkitMaskImage: `url(${src})`,
                  maskImage: `url(${src})`,
                }}
              />
            )}
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
          <span className="dial" aria-hidden />
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
