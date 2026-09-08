// =============================================================================
// PLACEHOLDER — generic male multi-pin SHELL
// =============================================================================
// TODO: pitch unknown until callipers.
// TODO: pin count, row spacing, keying, latch, and wire gauge unknown.
//
// This is NOT an AP1 drop-in. Honda cluster / engine-bay connectors are
// specific housings. Do not crimp this against a factory harness.
//
// Bay / plug callipers are REQUIRED before any print that touches the car.
// Print in PETG or ASA. Do NOT use PLA in the cabin.
// =============================================================================

$fn = 32;

// --- guessed geometry (WRONG until measured) --------------------------------
// Default 2.54 mm is a hobby pitch, almost certainly not the AP1 connector.
pin_pitch = 2.54;       // TODO: pitch unknown until callipers
rows = 2;
cols = 8;
pin_d = 0.8;            // TODO: pin diameter unknown
pin_len = 6.0;
row_pitch = 2.54;       // TODO: row spacing unknown

wall = 1.6;
cavity_extra = 1.2;
body_h = 10.0;
polarizer_w = 2.0;
polarizer_h = 3.0;

grid_w = (cols - 1) * pin_pitch;
grid_h = (rows - 1) * row_pitch;
body_w = grid_w + 2 * cavity_extra + 2 * wall;
body_d = grid_h + 2 * cavity_extra + 2 * wall + polarizer_h;

module pin_at(c, r) {
    translate([
        wall + cavity_extra + c * pin_pitch,
        wall + cavity_extra + r * row_pitch,
        body_h
    ])
        cylinder(h = pin_len, d = pin_d);
}

module male_shell() {
    difference() {
        union() {
            cube([body_w, body_d, body_h]);
            // Polarizing rib — SIDE UNKNOWN until the real plug is measured
            translate([body_w / 2 - polarizer_w / 2, body_d - 0.2, 2])
                cube([polarizer_w, polarizer_h, body_h - 4]);
        }
        // Cavity so this looks like a shell, not a solid brick
        translate([wall, wall, wall])
            cube([
                body_w - 2 * wall,
                body_d - 2 * wall - polarizer_h,
                body_h
            ]);
    }

    for (c = [0 : cols - 1], r = [0 : rows - 1])
        pin_at(c, r);
}

male_shell();
