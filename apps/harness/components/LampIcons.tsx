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
      <rect x="18.6" y="6.4" width="9.6" height="6.4" rx="0.7" />
      <rect x="35.8" y="6.4" width="9.6" height="6.4" rx="0.7" />
      <path fillRule="evenodd" d="M10.4 13.2h43.2v28.4H10.4z M15.2 17.8h33.6v19.2H15.2z" />
      <rect x="19.4" y="25.4" width="10.8" height="3.1" />
      <rect x="23.25" y="21.5" width="3.1" height="10.9" />
      <rect x="34.2" y="25.4" width="10.8" height="3.1" />
    </Plate>
  );
}

export function OilIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M4.2 25.2c0-8.4 6.2-14.6 15.2-14.6h6.2v4.6h-5.4c-5.2 0-8.6 3.6-8.6 10s3.4 10 8.6 10h5.4v4.6h-6.2C10.4 39.8 4.2 33.6 4.2 25.2z"
      />
      <rect x="28.4" y="10.6" width="10.2" height="4.4" rx="0.6" />
      <path fillRule="evenodd" d="M20.8 14.8h24.8v21.2H20.8z M25.2 19.2h16v12.4H25.2z" />
      <path
        fillRule="evenodd"
        d="M45.4 14.8 56.4 4.6l4.6 5-8.8 8.2z M48.6 16.4 56.2 9.4l1.6 1.8-6.4 5.6z"
      />
      <path d="M58.4 5.2c0 3.4 2.4 5.8 4.4 5.8s4.4-2.4 4.4-5.8c0-2.6-2-5.6-4.4-8.6-2.4 3-4.4 6-4.4 8.6z" />
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
      <path fillRule="evenodd" d="M18.4 7.4a13.6 13.6 0 1 0 .02 0zm0 6.2a7.4 7.4 0 1 0 .02 0z" />
      <rect x="29.2" y="20.4" width="28.8" height="6.6" rx="1.2" />
      <rect x="45.6" y="27" width="4.4" height="8.4" rx="0.7" />
      <rect x="52.4" y="27" width="4.4" height="11.8" rx="0.7" />
    </Plate>
  );
}

export function SeatbeltIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <circle cx="32" cy="8.4" r="6.6" />
      <path
        fillRule="evenodd"
        d="M18.4 16.6c0-2.4 6.1-4.8 13.6-4.8s13.6 2.4 13.6 4.8V45.4H18.4z M21.8 16 46.6 45.4h-8.8L20 22.6z"
      />
    </Plate>
  );
}

export function DoorIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M26.4 2.4h11.2c1.7 0 3.3 1 4.2 2.5L45.8 11.2v26.6c0 1.6-.9 3.1-2.3 4l-6.2 4.4H26.7l-6.2-4.4c-1.4-.9-2.3-2.4-2.3-4V11.2L22.2 4.9c.9-1.5 2.5-2.5 4.2-2.5z M29.6 9.6h4.8v7.2h-4.8z"
      />
      <path d="M18.2 20.2 4.4 27.6l2.8 5.2 12.4-6.6z" />
      <path d="M45.8 20.2 59.6 27.6l-2.8 5.2-12.4-6.6z" />
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
