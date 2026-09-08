#!/usr/bin/env bash
# Render placeholder STLs. Requires OpenSCAD (xvfb-run on headless boxes).
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
run_scad acrylic_face.scad acrylic_face.stl
run_scad rubber_buttons.scad rubber_buttons.stl
run_scad assembly.scad assembly.stl
echo "done"
