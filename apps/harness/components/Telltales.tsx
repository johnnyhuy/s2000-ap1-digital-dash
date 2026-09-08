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

function Word({
  label,
  size = 16,
  y = 31,
  x = 32,
}: {
  label: string;
  size?: number;
  y?: number;
  x?: number;
}) {
  return (
    <text
      x={x}
      y={y}
      textAnchor="middle"
      fontSize={size}
      fontWeight={700}
      letterSpacing="0.4"
      fill="currentColor"
      fontFamily="DejaVu Sans, Liberation Sans, Arial Narrow, sans-serif"
    >
      {label}
    </text>
  );
}

function Icon({ kind }: { kind: string }) {
  switch (kind) {
    case "turn_l":
      return <path d="M46 9 11 24l35 15v-9h12V18H46z" fill="currentColor" />;
    case "turn_r":
      return <path d="M18 9v9H6v12h12v9l35-15z" fill="currentColor" />;
    case "high_beam":
      return (
        <>
          <path d="M36 11c11.5 0 18 8 18 13s-6.5 13-18 13h-5V11h5z" fill="currentColor" />
          <path
            d="M8 15h22M6 20h24M6 24.5h24M6 29h24M8 34h22"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="square"
          />
        </>
      );
    case "abs":
      return <Word label="ABS" />;
    case "brake":
      return <Word label="BRAKE" size={13} />;
    case "battery":
      return (
        <>
          <rect x="14" y="16" width="36" height="22" rx="1.2" fill="currentColor" />
          <rect x="20" y="11" width="8" height="6" rx="0.4" fill="currentColor" />
          <rect x="36" y="11" width="8" height="6" rx="0.4" fill="currentColor" />
          <rect x="19" y="25.2" width="9" height="2.8" fill="#060402" />
          <rect x="36" y="25.2" width="9" height="2.8" fill="#060402" />
          <rect x="39.1" y="21.2" width="2.8" height="10.8" fill="#060402" />
        </>
      );
    case "oil":
      return (
        <>
          <path
            d="M12 22h22c1.4 0 3.2-1.1 7.2-6.2L48 9.6l3.2 3.4-6.6 7.2V36H12V22z"
            fill="currentColor"
          />
          <path d="M10 24c0-3.2 1.6-5.2 4.2-5.2H16v8h-4.4C10.4 26.8 10 25.6 10 24z" fill="currentColor" />
          <path
            d="M46.2 16.4c0 3.4 2.5 6.2 4.6 6.2s4.6-2.8 4.6-6.2c0-2.6-2-4.8-4.6-7.2-2.6 2.4-4.6 4.6-4.6 7.2z"
            fill="currentColor"
          />
        </>
      );
    case "cel":
      return (
        <>
          <path
            d="M12 22h6l3.2-7h9.2l2.2 7h15.2l3.6-4.6H58v7.4h3.4v12.2H58V40H12v-5.2H7.2V25.6H12z"
            fill="currentColor"
          />
          <rect x="7" y="28" width="6" height="7" fill="currentColor" />
          <text
            x="32"
            y="33.4"
            textAnchor="middle"
            fontSize="7.2"
            fontWeight={800}
            letterSpacing="0.55"
            fill="#060402"
            fontFamily="DejaVu Sans, Liberation Sans, Arial Narrow, sans-serif"
          >
            CHECK
          </text>
        </>
      );
    case "immobilizer":
      return (
        <>
          <circle cx="18" cy="24" r="10" fill="currentColor" />
          <circle cx="18" cy="24" r="4" fill="#060402" />
          <rect x="26" y="20.8" width="26" height="6.4" fill="currentColor" />
          <rect x="41.2" y="27" width="3.6" height="7.2" fill="currentColor" />
          <rect x="47.2" y="27" width="3.6" height="10" fill="currentColor" />
        </>
      );
    case "maint":
      return (
        <>
          <Word label="MAINT" size={11} y={22} />
          <Word label="REQ'D" size={11} y={36} />
        </>
      );
    case "eps":
      return <Word label="EPS" />;
    case "seatbelt":
      return (
        <>
          <circle cx="32" cy="11.5" r="6.4" fill="currentColor" />
          <path d="M20 20c0-2.2 3.6-4 12-4s12 1.8 12 4v7H20z" fill="currentColor" />
          <path d="M19 27h26v16H19z" fill="currentColor" />
          <path d="M22 20 42 42h-8L20 26z" fill="#060402" />
        </>
      );
    case "door":
      return (
        <>
          <path d="M25 7h14l6.4 7.2v25.6L39 47H25l-6.4-7.2V14.2z" fill="currentColor" />
          <rect x="28.4" y="11" width="7.2" height="5.2" fill="#060402" />
          <path d="M18.6 20.4 7.2 26.2l2.4 4.2 11.2-5.4z" fill="currentColor" />
          <path d="M45.4 20.4 56.8 26.2l-2.4 4.2-11.2-5.4z" fill="currentColor" />
        </>
      );
    case "srs":
      return <Word label="SRS" />;
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
            <svg viewBox="0 0 64 48" width="28" height="22" aria-hidden>
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
