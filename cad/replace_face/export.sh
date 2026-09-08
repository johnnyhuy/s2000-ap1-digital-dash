#!/usr/bin/env bash
# One SCAD → one solid STL. Assembly / plate previews are not exported.
# Requires OpenSCAD (xvfb-run on headless boxes).
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p stl

run_scad() {
    local src=$1
    local dst=$2
    echo "export $src -> stl/$dst"
    if command -v xvfb-run >/dev/null 2>&1; then
        xvfb-run -a openscad --export-format=binstl -o "stl/$dst" "$src"
    else
        openscad --export-format=binstl -o "stl/$dst" "$src"
    fi
}

run_scad backlight.scad backlight.stl
run_scad backlight_web.scad backlight_web.stl
run_scad acrylic_face.scad acrylic_face.stl
run_scad button_rocker.scad button_rocker.stl
run_scad button_sel.scad button_sel.stl
run_scad button_trip.scad button_trip.stl
echo "done"
