"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ClusterFace } from "./ClusterFace";
import { ReferencePanel } from "./ReferencePanel";
import {
  FACE_STYLES,
  FACE_STYLE_HINTS,
  FACE_STYLE_LABELS,
  parseFaceStyle,
  type FaceStyle,
} from "@/lib/faceStyle";
import {
  SCENARIO_LABELS,
  SCENARIOS,
  START_ODO_KM,
  followDisplay,
  frameAt,
  integrateOdo,
  snapDisplay,
  type DisplayState,
  type Scenario,
} from "@/lib/mockDrive";
import { telemetryToDict, type Telemetry } from "@/lib/protocol";

const HZ_FEEL = 48;

function styleFromSearch(): FaceStyle {
  if (typeof window === "undefined") return "ap1";
  return parseFaceStyle(new URLSearchParams(window.location.search).get("style"));
}

export function HarnessApp() {
  const [playing, setPlaying] = useState(true);
  const [scenario, setScenario] = useState<Scenario>("cruise");
  const [faceStyle, setFaceStyle] = useState<FaceStyle>("ap1");
  const [showRefs, setShowRefs] = useState(true);
  const [face, setFace] = useState<DisplayState>(() =>
    snapDisplay(frameAt(0, START_ODO_KM, "cruise"), START_ODO_KM),
  );
  const [raw, setRaw] = useState<Telemetry>(() => frameAt(0, START_ODO_KM, "cruise"));

  const playingRef = useRef(playing);
  const scenarioRef = useRef(scenario);
  const tRef = useRef(0);
  const odoRef = useRef(START_ODO_KM);
  const tripOriginRef = useRef(START_ODO_KM);
  const faceRef = useRef(face);
  const rawRef = useRef(raw);

  useEffect(() => {
    setFaceStyle(styleFromSearch());
  }, []);

  useEffect(() => {
    playingRef.current = playing;
  }, [playing]);

  useEffect(() => {
    scenarioRef.current = scenario;
  }, [scenario]);

  useEffect(() => {
    let raf = 0;
    let last = performance.now();
    let acc = 0;
    const tick = (now: number) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      if (playingRef.current) {
        tRef.current += dt;
        odoRef.current = integrateOdo(odoRef.current, rawRef.current.speed_kmh, dt);
      }
      acc += dt;
      const step = 1 / HZ_FEEL;
      if (acc >= step || !playingRef.current) {
        const useDt = playingRef.current ? Math.min(acc, 0.05) : 0.08;
        acc = 0;
        const target = frameAt(tRef.current, odoRef.current, scenarioRef.current);
        const next = followDisplay(faceRef.current, target, useDt, tripOriginRef.current);
        faceRef.current = next;
        rawRef.current = target;
        setFace(next);
        setRaw(target);
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, []);

  const applyScenario = useCallback((next: Scenario) => {
    setScenario(next);
    tRef.current = 0;
    const target = frameAt(0, odoRef.current, next);
    rawRef.current = target;
    setRaw(target);
  }, []);

  const applyStyle = useCallback((next: FaceStyle) => {
    setFaceStyle(next);
    if (typeof window === "undefined") return;
    const url = new URL(window.location.href);
    if (next === "ap1") url.searchParams.delete("style");
    else url.searchParams.set("style", next);
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
  }, []);

  const json = telemetryToDict(raw);

  return (
    <div className="harness">
      <section className="stage" data-refs={showRefs ? "on" : "off"}>
        <ClusterFace face={face} style={faceStyle} />
        {showRefs ? <ReferencePanel style={faceStyle} /> : null}
      </section>

      <section className="desk" aria-label="Harness controls">
        <div className="desk-row">
          <button
            type="button"
            className="primary"
            onClick={() => setPlaying((p) => !p)}
            aria-pressed={playing}
          >
            {playing ? "Pause" : "Play"}
          </button>
          <div className="presets" role="group" aria-label="Face style">
            {FACE_STYLES.map((id) => (
              <button
                key={id}
                type="button"
                className={id === faceStyle ? "preset on" : "preset"}
                onClick={() => applyStyle(id)}
                aria-pressed={id === faceStyle}
                title={FACE_STYLE_HINTS[id]}
              >
                {FACE_STYLE_LABELS[id]}
              </button>
            ))}
          </div>
          <div className="presets" role="group" aria-label="Scenario presets">
            {SCENARIOS.map((id) => (
              <button
                key={id}
                type="button"
                className={id === scenario ? "preset on" : "preset"}
                onClick={() => applyScenario(id)}
                aria-pressed={id === scenario}
              >
                {SCENARIO_LABELS[id]}
              </button>
            ))}
          </div>
          <button type="button" className="ghost" onClick={() => setShowRefs((v) => !v)}>
            {showRefs ? "Hide OEM refs" : "Show OEM refs"}
          </button>
        </div>

        <div className="desk-meta">
          <p>
            Client mock at ~{HZ_FEEL} Hz feel · frozen fields{" "}
            <code>rpm speed_kmh fuel_pct ect_c batt_v odo_km lamps</code>
          </p>
          <p>
            {playing ? "Live" : "Paused"} · {FACE_STYLE_LABELS[faceStyle]} ·{" "}
            {SCENARIO_LABELS[scenario]} · {Math.round(face.rpm)} r/min ·{" "}
            {Math.round(face.speed_kmh)} km/h
          </p>
        </div>
        <p className="desk-hint">{FACE_STYLE_HINTS[faceStyle]}</p>

        <pre className="json" tabIndex={0} aria-label="Current protocol JSON">
          {JSON.stringify(json, null, 2)}
        </pre>
      </section>
    </div>
  );
}
