// =============================================================================
// 3D printable modules — Option 1 replace-face stack
// =============================================================================
// One module = one solid. Downstream Blender remesh is expected; this file
// stays parametric. Callipers UNKNOWN. Not a verified AP1 drop-in.
//
// Cabin-facing hard parts: PETG or ASA. Do NOT use PLA in the cabin.
// Buttons: TPU 95A or cast silicone — not OEM rubber.
// =============================================================================

include <outline.scad>

module _through(h) {
    translate([0, 0, -eps])
        linear_extrude(h + 2 * eps)
            children();
}

module _cowl_web_2d() {
    // Inset so the web never shares an edge with the tray wall.
    difference() {
        offset(delta = -0.45)
            hood_2d();
        offset(delta = 0.35)
            lcd_window_2d();
        tach_slots_2d();
        offset(delta = 0.4)
            lamp_window_2d();
        button_caps_2d(1.2);
        align_holes_2d(align_hole_d + 0.8);
    }
}

module backlight() {
    // Tray shell only — one difference, no unioned ribs or pins.
    // Outer rim is offset(wall) around the 170×72.3 silhouette: a print wall,
    // NOT a measured bay clip and NOT a claimed AP1 fit.
    cavity_h = face_rebate_z - floor_t - 0.06;

    difference() {
        linear_extrude(tray_h)
            offset(delta = wall)
                hood_2d();

        translate([0, 0, face_rebate_z])
            linear_extrude(face_t + 1)
                offset(delta = face_pocket_clear)
                    hood_2d();

        translate([0, 0, floor_t])
            linear_extrude(cavity_h)
                hood_2d();

        // Switch wells — model UNKNOWN
        for (p = stem_xy())
            translate([p[0], p[1], -eps])
                cylinder(h = stem_well_h + eps, d = stem_well_d);

        // Cable / FPC escape — LOCATION UNKNOWN
        translate([
            face_w / 2 - cable_w / 2,
            -wall - eps,
            floor_t
        ])
            cube([cable_w, wall + 2 * eps, cable_h]);

        _through(tray_h)
            align_holes_2d();
    }
}

module backlight_web() {
    // Separate cowl-band insert. Drops on the tray floor. One extrusion.
    linear_extrude(min(3.8, face_rebate_z - floor_t - 0.5))
        _cowl_web_2d();
}

module acrylic_face() {
    // Mask plate — through-windows only. No back rebates (cleaner remesh).
    // Production: laser acrylic. Print proxy: PETG or ASA.
    // TEMP/FUEL are LCD-drawn horizontal bars inside lcd_window_2d()
    // (flanking the speedo). Do not cut vertical side-stack windows.
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
    }
}

module _button_solid(w, flange_extra) {
    // Single hull: cap → flange. No stem (switch UNKNOWN — add after measure).
    hull() {
        linear_extrude(eps)
            stadium_2d(w, btn_h);
        translate([0, 0, button_cap_t - eps])
            linear_extrude(eps)
                stadium_2d(w, btn_h);
        translate([
            -flange_extra,
            -flange_extra,
            button_cap_t + button_flange_t - eps
        ])
            linear_extrude(eps)
                stadium_2d(
                    w + 2 * flange_extra,
                    btn_h + 2 * flange_extra
                );
    }
}

module rocker_button() {
    difference() {
        _button_solid(rocker_w, button_flange_extra);
        translate([rocker_w / 2 - rocker_groove_w / 2, -eps, -eps])
            cube([rocker_groove_w, btn_h + 2 * eps, rocker_groove_d + eps]);
    }
}

module oval_button() {
    _button_solid(trip_w, min(button_flange_extra, sel_gap_mm * 0.4));
}

module sel_button() {
    oval_button();
}

module trip_button() {
    oval_button();
}

module rubber_buttons_print() {
    // F5 plate preview only — do not export this as one STL.
    rocker_button();
    translate([rocker_w + 8, 0, 0])
        sel_button();
    translate([rocker_w + 8 + trip_w + 8, 0, 0])
        trip_button();
}

module rubber_buttons_placed() {
    translate([0, 0, button_cap_t * 0.35])
        mirror([0, 0, 1]) {
            translate([rocker_x, btn_y, 0])
                rocker_button();
            translate([sel_x, btn_y, 0])
                sel_button();
            translate([trip_x, btn_y, 0])
                trip_button();
        }
}

module assembly(explode = 0) {
    // F5 preview only. Not a printable mesh.
    color([0.22, 0.22, 0.24])
        backlight();
    color([0.55, 0.52, 0.48])
        translate([0, 0, floor_t + explode * 0.35])
            backlight_web();
    color([0.82, 0.80, 0.74, 0.55])
        translate([0, 0, face_rebate_z + explode])
            acrylic_face();
    color([0.12, 0.12, 0.12])
        translate([0, 0, tray_h + explode * 2])
            rubber_buttons_placed();
    // F5 lock overlay only — LCD-drawn TEMP/FUEL, not a printable cut.
    color([0.95, 0.62, 0.12])
        translate([0, 0, face_rebate_z + explode + face_t + 0.2])
            linear_extrude(0.15)
                gauge_bars_2d();
}
