/** White-on-transparent ISO pictograms. Tint with currentColor. */

import type { ReactNode } from "react";

type IconProps = { className?: string; width?: number };

function Plate({
  className,
  width,
  viewBox = "0 0 64 48",
  children,
}: IconProps & { viewBox?: string; children: ReactNode }) {
  return (
    <svg
      className={className}
      viewBox={viewBox}
      width={width}
      height={width ? width * 0.75 : undefined}
      fill="currentColor"
      aria-hidden
    >
      {children}
    </svg>
  );
}

export function TurnLeftIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path d="M44 9.2 7.2 24 44 38.8v-7.6h12.4V16.8H44z" />
    </Plate>
  );
}

export function TurnRightIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path d="M20 9.2v7.6H7.6v14.4H20v7.6L56.8 24z" />
    </Plate>
  );
}

export function HighBeamIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <rect x="4.2" y="13.2" width="22.6" height="3.7" rx="0.4" />
      <rect x="3.2" y="22.15" width="24.4" height="3.7" rx="0.4" />
      <rect x="4.2" y="31.1" width="22.6" height="3.7" rx="0.4" />
      <path
        fillRule="evenodd"
        d="M33.6 8.2h6.4C54.8 8.2 61 15.4 61 24s-6.2 15.8-21 15.8h-6.4V8.2z M37.6 12.4v23.2h3.2c11.2 0 16-5.6 16-11.6S52 12.4 40.8 12.4h-3.2z"
      />
    </Plate>
  );
}

export function BatteryIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <rect x="17.4" y="5.2" width="10.4" height="7.2" rx="0.8" />
      <rect x="36.2" y="5.2" width="10.4" height="7.2" rx="0.8" />
      <path fillRule="evenodd" d="M8.8 12.8h46.4v30.4H8.8z M15.6 19.2h32.8v17.6H15.6z" />
      <rect x="18.6" y="25.6" width="11.6" height="3.4" />
      <rect x="22.7" y="21.4" width="3.4" height="11.8" />
      <rect x="34.2" y="25.6" width="11.6" height="3.4" />
    </Plate>
  );
}

export function OilIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M3.2 26.4c0-9.2 6.6-16 16.6-16h6.4v5.2H20.2c-5.8 0-9.6 4-9.6 10.8s3.8 10.8 9.6 10.8h6v5.2h-6.4C9.8 42.4 3.2 35.6 3.2 26.4z"
      />
      <rect x="27.8" y="11.2" width="11.4" height="5" rx="0.7" />
      <path fillRule="evenodd" d="M19.6 16h26.6v22.4H19.6z M24.4 20.8h17v12.8H24.4z" />
      <path
        fillRule="evenodd"
        d="M44.6 16.2 55.8 6.2l5.2 5.4-8.6 8z M48.2 17.8 56.2 10.4l1.8 1.9-6.4 5.8z"
      />
      <path d="M57.6 14.6c0 3.2 2.2 5.6 4.2 5.6s4.2-2.4 4.2-5.6c0-2.4-1.8-5.4-4.2-8.4-2.4 3-4.2 6-4.2 8.4z" />
    </Plate>
  );
}

const CHECK_HOLES =
  "M16.2 22.2h5.1v2.05h-3.05v4.5h3.05v2.05h-5.1zM22.2 22.2h2.05v3.35h1.7V22.2h2.05v8.6h-2.05v-3.2h-1.7v3.2H22.2zM29.1 22.2h5.05v2.05h-3v1.55h2.45v1.9H31.15v1.05h3v2.05h-5.05zM35.3 22.2h5.1v2.05h-3.05v4.5h3.05v2.05h-5.1zM41.5 22.2h2.1v3.15l2.55-3.15h2.35L45.3 26.4l3.35 4.4h-2.45l-2.05-2.7v2.7h-2.1z";

export function CelIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d={`M16.8 9.2h18.8c1.6 0 3 1.05 3.5 2.55l1.9 5.35h8.6l4.6-4.9h4.6v6.6h3.1v12.2h-3.1v6.8H8.4v-6.8H2.8V26.1h5.2v-4.2h6.6L15.4 11.7c.5-1.5 1.9-2.5 3.4-2.5z ${CHECK_HOLES}`}
      />
    </Plate>
  );
}

export function ImmobilizerIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path fillRule="evenodd" d="M17.2 5.6a16.6 16.6 0 1 0 .02 0zm0 7.4a9.2 9.2 0 1 0 .02 0z" />
      <rect x="30.4" y="19.2" width="30.6" height="8.4" rx="1.5" />
      <rect x="48.2" y="27.4" width="5.4" height="9.6" rx="0.8" />
      <rect x="55.8" y="27.4" width="5.4" height="13.4" rx="0.8" />
    </Plate>
  );
}

export function SeatbeltIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <circle cx="32" cy="8.2" r="6.5" />
      <path d="M29.2 13.8h5.6v3.4h-5.6z" />
      <path d="M17.4 20.2 12.6 28.4l4.2 2.2 3.6-6.8z" />
      <path d="M46.6 20.2 51.4 28.4l-4.2 2.2-3.6-6.8z" />
      <path
        fillRule="evenodd"
        d="M16.8 17.6 24.6 16.2 28 19h8l3.4-2.8 7.8 1.4-2.6 27.8H19.4z M20.4 15.2 49.6 45.4h-14L18.4 21.6z"
      />
      <path d="M21.6 15.4 47.4 45h-8.8L20.2 22.2z" />
    </Plate>
  );
}

export function DoorIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M25.4 2.2h13.2c2 0 3.8 1.15 4.7 2.95L47.4 11.4v26.4c0 1.7-1 3.3-2.6 4.3L38.2 46H25.8l-6.6-3.9c-1.6-1-2.6-2.6-2.6-4.3V11.4L20.7 5.15C21.6 3.35 23.4 2.2 25.4 2.2z M27.2 7.8h9.6v9.4h-9.6z"
      />
      <path d="M18.2 20.6 2.8 28.6l3.6 6 13.6-7.2z" />
      <path d="M45.8 20.6 61.2 28.6l-3.6 6-13.6-7.2z" />
    </Plate>
  );
}

export const PICTOGRAMS = {
  turn_l: TurnLeftIcon,
  turn_r: TurnRightIcon,
  high_beam: HighBeamIcon,
  battery: BatteryIcon,
  oil: OilIcon,
  cel: CelIcon,
  immobilizer: ImmobilizerIcon,
  seatbelt: SeatbeltIcon,
  door: DoorIcon,
} as const;
