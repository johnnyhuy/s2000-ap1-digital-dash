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
      <path d="M50 7.2 3.2 24 50 40.8v-9.6H61.2V16.8H50z" />
    </Plate>
  );
}

export function TurnRightIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path d="M14 7.2v9.6H2.8v14.4H14v9.6L60.8 24z" />
    </Plate>
  );
}

export function HighBeamIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M36.4 8.4h7.2C56.4 8.4 62 16 62 24s-5.6 15.6-18.4 15.6h-7.2V8.4z M40.6 12.6v22.8h3c9.2 0 13.2-5.2 13.2-11.4S52.8 12.6 43.6 12.6h-3z"
      />
      <rect x="3.6" y="10.8" width="26.4" height="2.4" rx="0.4" />
      <rect x="2" y="16.4" width="28" height="2.4" rx="0.4" />
      <rect x="2" y="22.8" width="28" height="2.4" rx="0.4" />
      <rect x="2" y="29.2" width="28" height="2.4" rx="0.4" />
      <rect x="3.6" y="34.8" width="26.4" height="2.4" rx="0.4" />
    </Plate>
  );
}

export function BatteryIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <rect x="20.4" y="7.6" width="9.2" height="6.2" rx="0.7" />
      <rect x="34.4" y="7.6" width="9.2" height="6.2" rx="0.7" />
      <path fillRule="evenodd" d="M11.6 14.6h40.8v25.2H11.6z M16.2 19h31.6v16.4H16.2z" />
      <rect x="19.2" y="25.6" width="11.2" height="3" />
      <rect x="23.3" y="21.4" width="3" height="11.4" />
      <rect x="34.4" y="25.6" width="11.2" height="3" />
    </Plate>
  );
}

export function OilIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M4.6 24.6c0-8 6-14 14.6-14h6.6v4.8h-5.6c-4.8 0-8.2 3.4-8.2 9.2s3.4 9.2 8.2 9.2h5.6v4.8h-6.6C10.6 38.6 4.6 32.6 4.6 24.6z"
      />
      <path fillRule="evenodd" d="M20.4 14.2h24.4v20.4H20.4z M24.6 18.4h16v12H24.6z" />
      <path fillRule="evenodd" d="M44.8 14.2 58.2 2.8l5.4 5.8-10.2 8.6z M48.2 16.2 57.4 8.4l1.8 2-7.6 6.4z" />
      <path d="M53.6 13.8c0 3.4 2.4 5.8 4.4 5.8s4.4-2.4 4.4-5.8c0-2.6-2-5.6-4.4-8.4-2.4 2.8-4.4 5.8-4.4 8.4z" />
    </Plate>
  );
}

export function CelIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M17.6 8.8h20.4c1.5 0 2.8 1 3.3 2.4l2.2 6.2h9.2l5.2-5.6h5.2v7.4h3.4v13.2h-3.4v7.4H7.8v-7.4H2.2V26.4h5.6v-4.4h7.2L16.2 11.2c.5-1.4 1.8-2.4 3.3-2.4z M16.4 23.8h31.6v10.2H16.4z"
      />
      <path d="M19 25.6h3.4v6.6H19zm6.6 0h3.4v6.6h-3.4zm6.6 0h3.4v6.6h-3.4zm6.6 0h3.4v6.6h-3.4zm6.6 0h3.4v6.6h-3.4z" />
    </Plate>
  );
}

export function ImmobilizerIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path fillRule="evenodd" d="M17.2 8.6a13.2 13.2 0 1 0 .02 0zm0 6.4a6.8 6.8 0 1 0 .02 0z" />
      <rect x="27.2" y="19.6" width="30.6" height="6.4" rx="1.1" />
      <rect x="44.6" y="26" width="4.6" height="8.8" rx="0.6" />
      <rect x="51.8" y="26" width="4.6" height="12.2" rx="0.6" />
    </Plate>
  );
}

export function SeatbeltIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path fillRule="evenodd" d="M32 2.4a7.2 7.2 0 1 0 .02 0zm0 4.4a2.8 2.8 0 1 0 .02 0z" />
      <path
        fillRule="evenodd"
        d="M17.6 16.8c0-2.4 6.4-4.8 14.4-4.8s14.4 2.4 14.4 4.8V44.4H17.6z M21.2 16.2 46.4 44.4h-9.6L19.2 23.2z"
      />
    </Plate>
  );
}

export function DoorIcon(props: IconProps) {
  return (
    <Plate {...props}>
      <path
        fillRule="evenodd"
        d="M24.8 2.4h14.4c1.5 0 2.9.8 3.7 2l5.2 6.6v27.8c0 1.5-.8 2.9-2 3.7l-6.6 5.2H24.7l-6.6-5.2c-1.2-.8-2-2.2-2-3.7V11c0-1.5.8-2.9 2-3.7z M28.4 10.6h7.2v6.4h-7.2z"
      />
      <path d="M16.4 19.2 1.4 27.2l4 6.2 12.8-6.8z" />
      <path d="M47.6 19.2 62.6 27.2l-4 6.2-12.8-6.8z" />
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
