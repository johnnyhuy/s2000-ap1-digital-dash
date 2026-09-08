#!/usr/bin/env python3
"""Record the ID.4 intro → live demo as a small GIF (optional MP4 via ffmpeg).

  python src/record_demo.py
  python src/record_demo.py shots/demo_intro_live.gif
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gauge_ui import main as gauge_main


def _maybe_mp4(gif: Path) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return
    mp4 = gif.with_suffix(".mp4")
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(gif),
        "-movflags",
        "+faststart",
        "-pix_fmt",
        "yuv420p",
        str(mp4),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        return
    if mp4.exists() and 1024 < mp4.stat().st_size < 4_000_000:
        print(mp4)
    elif mp4.exists():
        mp4.unlink()


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    dest = Path(args[0] if args else "shots/demo_intro_live.gif")
    gauge_main(["--smoke", "--gif", str(dest)])
    _maybe_mp4(dest)


if __name__ == "__main__":
    main()
