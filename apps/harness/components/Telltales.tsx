import type { LampMap } from "@/lib/protocol";
import { BATT_LOW_V } from "@/lib/protocol";

type Tone = "red" | "amber" | "green" | "blue";

type LampSpec = {
  kind: string;
  key: string;
  tone: Tone;
  label: string;
};

export const LAMP_STRIP: LampSpec[] = [
  { kind: "turn_l", key: "turn_l", tone: "green", label: "Left turn" },
  { kind: "high_beam", key: "high_beam", tone: "blue", label: "High beam" },
  { kind: "abs", key: "abs", tone: "amber", label: "ABS" },
  { kind: "brake", key: "brake", tone: "red", label: "BRAKE" },
  { kind: "battery", key: "batt_warn", tone: "red", label: "Battery" },
  { kind: "oil", key: "oil", tone: "red", label: "Oil" },
  { kind: "cel", key: "cel", tone: "amber", label: "Check engine" },
  { kind: "immobilizer", key: "immobilizer", tone: "green", label: "Immobilizer" },
  { kind: "maint", key: "maint", tone: "amber", label: "MAINT REQ'D" },
  { kind: "eps", key: "eps", tone: "amber", label: "EPS" },
  { kind: "seatbelt", key: "seatbelt", tone: "red", label: "Seatbelt" },
  { kind: "door", key: "door", tone: "red", label: "Door" },
  { kind: "srs", key: "srs", tone: "red", label: "SRS" },
  { kind: "turn_r", key: "turn_r", tone: "green", label: "Right turn" },
];

const TONE: Record<Tone, string> = {
  red: "#d6221e",
  amber: "#e48a1a",
  green: "#2cc458",
  blue: "#1c56d6",
};

const GHOST = "#282420";

function Icon({ kind }: { kind: string }) {
  switch (kind) {
    case "turn_l":
      return <path d="M18 6 4 14l14 8V6z" fill="currentColor" />;
    case "turn_r":
      return <path d="M6 6l14 8-14 8V6z" fill="currentColor" />;
    case "high_beam":
      return (
        <>
          <circle cx="10" cy="14" r="6" fill="none" stroke="currentColor" strokeWidth="1.8" />
          <path
            d="M10 8a6 6 0 0 0 0 12M17 8l7-1M17 12l7-.4M17 16l7 .4M17 20l7 1"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </>
      );
    case "abs":
      return (
        <text x="14" y="18" textAnchor="middle" fontSize="8" fontWeight="700" fill="currentColor">
          ABS
        </text>
      );
    case "brake":
      return (
        <text x="14" y="18" textAnchor="middle" fontSize="7" fontWeight="700" fill="currentColor">
          BRAKE
        </text>
      );
    case "battery":
      return (
        <>
          <rect x="6" y="10" width="16" height="10" rx="1.5" fill="none" stroke="currentColor" strokeWidth="1.6" />
          <rect x="9" y="7.5" width="4" height="2.5" fill="currentColor" />
          <rect x="15" y="7.5" width="4" height="2.5" fill="currentColor" />
          <path d="M10 15h3M15 15h3M16.5 13.5v3" stroke="currentColor" strokeWidth="1.4" />
        </>
      );
    case "oil":
      return (
        <>
          <rect x="6" y="12" width="11" height="7" rx="1.2" fill="currentColor" />
          <path d="M16 12l6-4 1.6 1.6-5 4z" fill="currentColor" />
          <circle cx="8" cy="21" r="1.6" fill="currentColor" />
        </>
      );
    case "cel":
      return (
        <>
          <rect x="6" y="10" width="16" height="9" rx="1.4" fill="none" stroke="currentColor" strokeWidth="1.5" />
          <path d="M6 14.5 3 17M22 14.5 25 17" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <text x="14" y="17" textAnchor="middle" fontSize="5" fontWeight="700" fill="currentColor">
            CHECK
          </text>
        </>
      );
    case "immobilizer":
      return (
        <path
          d="M10 8h8v5H10zm2 5v4l2 3 2-3v-4"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinejoin="round"
        />
      );
    case "maint":
      return (
        <text x="14" y="18" textAnchor="middle" fontSize="6.2" fontWeight="700" fill="currentColor">
          MAINT
        </text>
      );
    case "eps":
      return (
        <text x="14" y="18" textAnchor="middle" fontSize="8" fontWeight="700" fill="currentColor">
          EPS
        </text>
      );
    case "seatbelt":
      return (
        <path
          d="M14 6a3 3 0 1 1 0 6 3 3 0 0 1 0-6zm-6 16 6-10 6 10"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.7"
          strokeLinejoin="round"
        />
      );
    case "door":
      return (
        <path
          d="M8 6h10l3 4v12H8zM18 14h3"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
        />
      );
    case "srs":
      return (
        <text x="14" y="18" textAnchor="middle" fontSize="8" fontWeight="700" fill="currentColor">
          SRS
        </text>
      );
    default:
      return null;
  }
}

export function TelltaleStrip({
  lamps,
  battV,
}: {
  lamps: LampMap;
  battV: number;
}) {
  return (
    <div className="lamp-strip" role="group" aria-label="OEM telltales">
      {LAMP_STRIP.map((spec) => {
        const extra = spec.key === "batt_warn" && battV < BATT_LOW_V;
        const lit = Boolean(lamps[spec.key] || extra);
        const color = lit ? TONE[spec.tone] : GHOST;
        return (
          <span
            key={spec.kind}
            className={`telltale${lit ? " telltale-on" : ""}`}
            title={spec.label}
            style={{ color, ["--lamp" as string]: color }}
          >
            <svg viewBox="0 0 28 24" width="28" height="22" aria-hidden>
              <Icon kind={spec.kind} />
            </svg>
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
