// =============================================================================
// 3D printable modules — Option 1 replace-face stack
// =============================================================================
// PLACEHOLDER geometry. Callipers UNKNOWN. Not a verified AP1 drop-in.
// Print cabin-facing parts in PETG or ASA. Do NOT use PLA in the cabin.
// Buttons: TPU 95A or cast silicone — still not a factory rubber replica.
// =============================================================================

include <outline.scad>

module _through(h) {
    translate([0, 0, -eps])
        linear_extrude(h + 2 * eps)
            children();
}

module _cowl_web_2d() {
    // Inset so the web does not share a face with the tray wall (manifold).
    difference() {
        offset(delta = -0.45)
            hood_2d();
        offset(delta = 0.35)
            lcd_window_2d();
        tach_slots_2d();
        offset(delta = 0.4)
            lamp_window_2d();
        button_caps_2d(1.2);
        align_holes_2d(align_boss_d + 0.8);
    }
}

module backlight() {
    // Rear light tray / diffuser frame.
    // Outer rim is offset(wall) around the 170×72.3 silhouette — a print wall,
    // NOT a measured bay clip and NOT a claimed AP1 fit.
    cavity_h = face_rebate_z - floor_t - 0.06;
    web_h = min(3.8, cavity_h - 0.4);

    union() {
    difference() {
        linear_extrude(tray_h)
            offset(delta = wall)
                hood_2d();

        // Face rebate: OEM silhouette + slip. Acrylic drops in flush.
        translate([0, 0, face_rebate_z])
            linear_extrude(face_t + 1)
                offset(delta = face_pocket_clear)
                    hood_2d();

        // Main light cavity — stops shy of the rebate plane
        translate([0, 0, floor_t])
            linear_extrude(cavity_h)
                hood_2d();

        // Button stem / future-switch wells — switch model UNKNOWN
        for (p = stem_xy())
            translate([p[0], p[1], -eps])
                cylinder(h = stem_well_h + eps, d = stem_well_d);

        // Cable / FPC escape — LOCATION UNKNOWN (bottom-centre guess)
        translate([
            face_w / 2 - cable_w / 2,
            -wall - eps,
            floor_t
        ])
            cube([cable_w, wall + 2 * eps, cable_h]);
    }

    // Internals after the cavity cut; sunk into the floor so the union overlaps
    translate([0, 0, floor_t - 0.25])
        linear_extrude(web_h + 0.25)
            _cowl_web_2d();

    for (p = align_xy()) {
        translate([p[0], p[1], floor_t - 0.25])
            cylinder(h = cavity_h + 0.25, d = align_boss_d);
        translate([p[0], p[1], face_rebate_z - 0.15])
            cylinder(h = align_pin_h + 0.15, d = align_pin_d);
    }
    }
}

module acrylic_face() {
    // Translucent / opaque mask. Production: laser acrylic. Print proxy: PETG/ASA.
    difference() {
        linear_extrude(face_t)
            hood_2d();

        _through(face_t)
            lcd_window_2d();

        _through(face_t)
            tach_slots_2d();

        _through(face_t)
            lamp_window_2d();

        _through(face_t)
            button_caps_2d(button_clear);

        _through(face_t)
            align_holes_2d();

        // Back-side flange rebate (z = 0 is the tray side)
        translate([0, 0, -eps])
            linear_extrude(button_flange_t + 0.15)
                button_caps_2d(button_clear + button_flange_extra * 0.35);
    }
}

module _button_body(w, extra_stems, flange_extra = button_flange_extra) {
    overlap = 0.08;
    union() {
        linear_extrude(button_cap_t)
            stadium_2d(w, btn_h);
        translate([
            -flange_extra,
            -flange_extra,
            button_cap_t - overlap
        ])
            linear_extrude(button_flange_t + overlap)
                stadium_2d(
                    w + 2 * flange_extra,
                    btn_h + 2 * flange_extra
                );
        for (sx = extra_stems)
            translate([
                sx,
                btn_h / 2,
                button_cap_t + button_flange_t - overlap
            ])
                cylinder(h = button_stem_h + overlap, d = button_stem_d);
    }
}

module rocker_button() {
    difference() {
        _button_body(rocker_w, [rocker_w * 0.28, rocker_w * 0.72]);
        // − / + split — one rubber part; PUSH CANCEL is a push on this rocker
        translate([rocker_w / 2 - rocker_groove_w / 2, -eps, -eps])
            cube([rocker_groove_w, btn_h + 2 * eps, rocker_groove_d + eps]);
    }
}

module oval_button() {
    // Flange stays inside the 1 mm PLACEHOLDER SEL–TRIP gap
    _button_body(trip_w, [trip_w / 2], min(button_flange_extra, sel_gap_mm * 0.4));
}

module rubber_buttons_print() {
    // Plate layout — not in-car spacing
    rocker_button();
    translate([rocker_w + 8, 0, 0])
        oval_button();
    translate([rocker_w + 8 + trip_w + 8, 0, 0])
        oval_button();
}

module rubber_buttons_placed() {
    // Face coordinates. Cap toward +Z (driver), stem toward the tray.
    translate([0, 0, button_cap_t * 0.35])
        mirror([0, 0, 1]) {
            translate([rocker_x, btn_y, 0])
                rocker_button();
            translate([sel_x, btn_y, 0])
                oval_button();
            translate([trip_x, btn_y, 0])
                oval_button();
        }
}

module assembly(explode = 0) {
    // Preview only. Colours are not print materials.
    color([0.22, 0.22, 0.24])
        backlight();

    color([0.82, 0.80, 0.74, 0.55])
        translate([0, 0, face_rebate_z + explode])
            acrylic_face();

    color([0.12, 0.12, 0.12])
        translate([0, 0, tray_h + explode * 2])
            rubber_buttons_placed();
}
