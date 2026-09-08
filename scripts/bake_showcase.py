#!/usr/bin/env python3
"""Bake cluster stills + a short intro→live GIF/WebM for the README.

Uses the same draw_frame path as `python src/gauge_ui.py --smoke --screenshot`.
Does not change protocol field names or the OEM face.

  python scripts/bake_showcase.py
  python scripts/bake_showcase.py --shots-only
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SHOTS = ROOT / "shots"
ASSETS = ROOT / "docs" / "assets"

sys.path.insert(0, str(SRC))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bake S2000 digital dash showcase media")
    p.add_argument("--shots-only", action="store_true", help="Regenerate shots/ PNGs only")
    p.add_argument("--fps", type=int, default=30, help="Intro GIF/WebM frame rate (30–60)")
    p.add_argument("--width", type=int, default=960, help="Encoded media width")
    p.add_argument("--live-s", type=float, default=2.0, help="Seconds of live after reveal")
    p.add_argument("--webm-fps", type=int, default=60, help="VP9 encode frame rate")
    return p.parse_args(argv)


def _init_renderer():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    from gauge_ui import (
        DisplayState,
        build_fonts,
        draw_frame,
        init_pygame,
        intro_duration_s,
        intro_phase_at,
        sample_telem,
        write_screenshots,
    )

    pygame, _screen = init_pygame(windowed=True, headless=True)
    fonts = build_fonts(pygame)
    face = DisplayState()
    telem = sample_telem()
    face.snap(telem)
    face.trip_origin = telem.odo_km - 128.4
    face.trip_km = 128.4
    return pygame, fonts, face, write_screenshots, draw_frame, intro_phase_at, intro_duration_s


def bake_shots(pygame, fonts, face, write_screenshots) -> list[Path]:
    paths = write_screenshots(pygame, fonts, face, SHOTS)
    for path in paths:
        print(path)
    return paths


def bake_intro_frames(
    pygame,
    fonts,
    face,
    draw_frame,
    intro_phase_at,
    intro_duration_s,
    dest: Path,
    fps: int,
    live_s: float,
) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    canvas = pygame.Surface((1920, 1080))
    duration = intro_duration_s() + live_s
    n = max(1, int(round(duration * fps)))
    written: list[Path] = []
    base_rpm = face.rpm
    base_speed = face.speed_kmh
    for i in range(n):
        t = i / fps
        phase, local_t = intro_phase_at(t)
        if phase == "live":
            # Smooth live lerp so the loop is not a static still
            live_t = t - intro_duration_s()
            wave = 0.5 + 0.5 * math.sin(live_t * 2.4)
            face.rpm = base_rpm + 900.0 * (wave - 0.5)
            face.speed_kmh = base_speed + 8.0 * (wave - 0.5)
        draw_frame(pygame, fonts, canvas, face, phase, local_t)
        path = dest / f"frame_{i:04d}.png"
        pygame.image.save(canvas, str(path))
        written.append(path)
    face.rpm = base_rpm
    face.speed_kmh = base_speed
    return written


def _run_ffmpeg(args: list[str]) -> None:
    print("+", " ".join(args))
    subprocess.run(args, check=True)


def encode_media(frame_dir: Path, fps: int, width: int, webm_fps: int | None = None) -> tuple[Path, Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    pattern = str(frame_dir / "frame_%04d.png")
    gif = ASSETS / "intro-live.gif"
    webm = ASSETS / "intro-live.webm"
    scale = f"scale={width}:-1:flags=lanczos"
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            pattern,
            "-vf",
            f"{scale},split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];[s1][p]paletteuse=dither=sierra2_4a",
            "-loop",
            "0",
            str(gif),
        ]
    )
    wfps = webm_fps or max(fps, 30)
    _run_ffmpeg(
        [
            "ffmpeg",
            "-y",
            "-framerate",
            str(fps),
            "-i",
            pattern,
            "-vf",
            f"{scale},minterpolate=fps={wfps}:mi_mode=blend" if wfps > fps else scale,
            "-c:v",
            "libvpx-vp9",
            "-b:v",
            "0",
            "-crf",
            "32",
            "-an",
            str(webm),
        ]
    )
    return gif, webm


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    (
        pygame,
        fonts,
        face,
        write_screenshots,
        draw_frame,
        intro_phase_at,
        intro_duration_s,
    ) = _init_renderer()

    bake_shots(pygame, fonts, face, write_screenshots)
    if args.shots_only:
        pygame.quit()
        return

    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found — stills written, skip GIF/WebM", file=sys.stderr)
        pygame.quit()
        raise SystemExit(1)

    with tempfile.TemporaryDirectory(prefix="ap1-intro-") as tmp:
        frames = bake_intro_frames(
            pygame,
            fonts,
            face,
            draw_frame,
            intro_phase_at,
            intro_duration_s,
            Path(tmp),
            args.fps,
            args.live_s,
        )
        print(f"wrote {len(frames)} intro frames")
        gif, webm = encode_media(Path(tmp), args.fps, args.width, args.webm_fps)
        print(gif, gif.stat().st_size)
        print(webm, webm.stat().st_size)

    pygame.quit()


if __name__ == "__main__":
    main()
