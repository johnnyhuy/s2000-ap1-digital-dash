// =============================================================================
// PLACEHOLDER — NOT a cabin-ready print
// =============================================================================
// Overlay-only 7" frame. For the full arched replace-face stack see
// cad/replace_face/ — do not mix the two envelopes.
//
// 7" landscape AMOLED bezel / frame (Wisecoco-class panel, Phase 1 bench).
//
// Bay callipers are REQUIRED before any in-car / cabin print.
// These numbers are typical-datasheet guesses, not a measured AP1 bay or
// a measured panel. Do not treat this as production geometry.
//
// Print in PETG or ASA. Do NOT use PLA in the cabin (heat soak, creep,
// warpage against a sun-loaded dash).
// =============================================================================

$fn = 48;

// --- guessed panel envelope (MEASURE THE REAL PART) -------------------------
// Overall module ~164 × 100 mm; active area ~154 × 87 mm (16:9 / 7").
panel_w = 164.0;
panel_h = 100.0;
panel_t = 4.0;          // stack thickness guess — callipers required
active_w = 154.0;
active_h = 87.0;

bezel_margin = 8.0;     // frame around the module
lip = 2.0;              // retention lip over the glass edge
frame_t = 8.0;
pocket_clear = 0.5;     // slip fit guess — measure
corner_r = 4.0;

// Outer frame
outer_w = panel_w + 2 * bezel_margin;
outer_h = panel_h + 2 * bezel_margin;

// Cable escape (placeholder location — confirm on the real FPC/HDMI tail)
cable_w = 22.0;
cable_h = 6.0;

// Mounting ears (PLACEHOLDER hole pattern — do not drill the bay from this)
ear_w = 14.0;
ear_h = 12.0;
ear_hole = 3.2;         // M3 clearance guess

module round_rect(w, h, t, r) {
    rr = min(r, w / 2, h / 2);
    hull() {
        for (x = [rr, w - rr], y = [rr, h - rr])
            translate([x, y, 0])
                cylinder(h = t, r = rr);
    }
}

module mounting_ear() {
    difference() {
        round_rect(ear_w, ear_h, frame_t, 2.0);
        translate([ear_w / 2, ear_h / 2, -0.1])
            cylinder(h = frame_t + 0.2, d = ear_hole);
    }
}

module bezel() {
    difference() {
        union() {
            round_rect(outer_w, outer_h, frame_t, corner_r + 2);

            // Four guessed ears — positions are NOT bay-accurate
            translate([-ear_w + 2, outer_h / 2 - ear_h / 2, 0])
                mounting_ear();
            translate([outer_w - 2, outer_h / 2 - ear_h / 2, 0])
                mounting_ear();
            translate([outer_w / 2 - ear_w / 2, -ear_h + 2, 0])
                mounting_ear();
            translate([outer_w / 2 - ear_w / 2, outer_h - 2, 0])
                mounting_ear();
        }

        // Panel pocket (from the back)
        translate([
            bezel_margin - pocket_clear / 2,
            bezel_margin - pocket_clear / 2,
            frame_t - panel_t
        ])
            round_rect(
                panel_w + pocket_clear,
                panel_h + pocket_clear,
                panel_t + 0.2,
                corner_r
            );

        // Active-area viewing window (from the front)
        translate([
            (outer_w - active_w) / 2,
            (outer_h - active_h) / 2,
            -0.1
        ])
            round_rect(active_w, active_h, frame_t + 0.2, 1.5);

        // Cable / mini-HDMI tail escape (bottom centre — GUESS)
        translate([
            (outer_w - cable_w) / 2,
            -0.1,
            frame_t - panel_t
        ])
            cube([cable_w, bezel_margin + cable_h, panel_t + 0.2]);
    }

    // Retention lip drawn as the leftover ring (panel sits behind the window).
    // Front glass flush vs. recessed is UNKNOWN until the bay is callipered.
}

bezel();
