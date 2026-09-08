import { HarnessApp } from "@/components/HarnessApp";

export default function Home() {
  return (
    <div className="shell">
      <p className="disclaimer" role="note">
        <strong>Unofficial DIY — no affiliation.</strong> This is an enthusiast
        bench demo and is <strong>not affiliated with, endorsed by, or associated
        with Honda Motor Co., Ltd.</strong> Honda, S2000, AP1, AP2 and related marks
        are trademarks of their respective owners. The on-screen odometer is
        display-only; keep the OEM cluster plugged for the legal odometer.
      </p>

      <header className="masthead">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/docs/assets/honda-unofficial-mark.svg"
          alt="Unofficial geometric H mark — not Honda trademark artwork"
        />
        <div>
          <h1>S2000 Digital Dash</h1>
          <p>Web cluster harness · AP1 / AP2 face styles · frozen JSON protocol</p>
        </div>
      </header>

      <main>
        <HarnessApp />
      </main>

      <footer className="colophon">
        <p>
          Selectable AP1 (straight TEMP/FUEL) or AP2 (arched side gauges) face.
          Not a product, not car-ready, not a replacement for the factory cluster.
        </p>
        <p>
          <a href="https://github.com/johnnyhuy/s2000-ap1-digital-dash">
            johnnyhuy/s2000-ap1-digital-dash
          </a>
          {" · "}
          <a href="/harness">/harness</a>
        </p>
      </footer>
    </div>
  );
}
