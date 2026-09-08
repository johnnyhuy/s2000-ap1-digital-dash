// =============================================================================
// PLACEHOLDER — generic female multi-pin SHELL
// =============================================================================
// TODO: pitch unknown until callipers.
// TODO: pin count, row spacing, keying, latch, and wire gauge unknown.
//
// This is NOT an AP1 drop-in. Do not mate this to a factory Honda plug
// and do not treat it as a cluster-harness replica.
//
// Bay / plug callipers are REQUIRED before any print that touches the car.
// Print in PETG or ASA. Do NOT use PLA in the cabin.
// =============================================================================

$fn = 32;

// Must stay in lock-step with connector_male_placeholder.scad guesses.
// Both files are still wrong until the real connector is measured.
pin_pitch = 2.54;       // TODO: pitch unknown until callipers
rows = 2;
cols = 8;
pin_d = 0.8;            // TODO: socket ID unknown
row_pitch = 2.54;       // TODO: row spacing unknown

wall = 1.6;
cavity_extra = 1.2;
slip = 0.3;             // extra on the ID so the male *might* start — still a guess
body_h = 12.0;
polarizer_w = 2.4;
polarizer_h = 3.4;
latch_w = 8.0;
latch_t = 1.4;

grid_w = (cols - 1) * pin_pitch;
grid_h = (rows - 1) * row_pitch;
body_w = grid_w + 2 * cavity_extra + 2 * wall + slip;
body_d = grid_h + 2 * cavity_extra + 2 * wall + polarizer_h + slip;

module socket_at(c, r) {
    translate([
        wall + cavity_extra + slip / 2 + c * pin_pitch,
        wall + cavity_extra + slip / 2 + r * row_pitch,
        -0.1
    ])
        cylinder(h = body_h + 0.2, d = pin_d + 0.3);
}

module female_shell() {
    difference() {
        union() {
            cube([body_w, body_d, body_h]);
            // Crude latch tab — geometry is fiction until callipers
            translate([body_w / 2 - latch_w / 2, -latch_t, body_h * 0.35])
                cube([latch_w, latch_t + 0.2, body_h * 0.4]);
        }

        // Mating pocket
        translate([wall, wall, wall])
            cube([
                body_w - 2 * wall,
                body_d - 2 * wall - polarizer_h,
                body_h
            ]);

        // Polarizer slot (mirrors the male rib — side still a guess)
        translate([
            body_w / 2 - polarizer_w / 2,
            body_d - polarizer_h - 0.2,
            1.5
        ])
            cube([polarizer_w, polarizer_h + 0.4, body_h]);

        for (c = [0 : cols - 1], r = [0 : rows - 1])
            socket_at(c, r);
    }
}

female_shell();
