// =============================================================================
// 2D OEM silhouette + window helpers (replace-face)
// =============================================================================
// Matches refs/flat/DIMENSIONS.md and src/gauge_ui.py hood_outer_points():
// flat bottom, rectangular 58–72% notches, parabola y% = 28 u².
// All sizes still ESTIMATED / PLACEHOLDER — see dims.scad.
// =============================================================================

include <dims.scad>

function arch_points(x0, x1, y_peak, y_spring, n = arch_steps) =
    [for (i = [0 : n])
        let (t = i / n, u = 2 * t - 1)
        [x0 + (x1 - x0) * t, y_peak - (y_peak - y_spring) * u * u]
    ];

// Counter-clockwise from bottom-left. Notch-top is colinear with the inset
// side; kept so the point list matches the pygame lock.
function hood_points() =
    concat(
        [
            [0, 0],
            [face_w, 0],
            [face_w, notch_bot_y],
            [face_w - step_w, notch_bot_y],
            [face_w - step_w, notch_top_y],
            [face_w - step_w, spring_y]
        ],
        arch_points(face_w - step_w, step_w, face_h, spring_y),
        [
            [step_w, spring_y],
            [step_w, notch_top_y],
            [step_w, notch_bot_y],
            [0, notch_bot_y]
        ]
    );

function lcd_points() =
    concat(
        [
            [lcd_x, lcd_bot_y],
            [lcd_x + lcd_w, lcd_bot_y],
            [lcd_x + lcd_w, lcd_spring_y]
        ],
        arch_points(lcd_x + lcd_w, lcd_x, lcd_peak_y, lcd_spring_y),
        [[lcd_x, lcd_spring_y]]
    );

module hood_2d() {
    polygon(hood_points());
}

module lcd_2d() {
    polygon(lcd_points());
}

module lcd_window_2d() {
    // Keep a continuous frame — the raw LCD polygon breaches the hood
    // arch at both springs (lcd_spring sits above hood spring).
    intersection() {
        offset(delta = -lcd_frame_mm)
            hood_2d();
        lcd_2d();
    }
}

module stadium_2d(w, h) {
    r = min(w, h) / 2;
    hull() {
        translate([r, r]) circle(r = r);
        translate([w - r, r]) circle(r = r);
    }
}

module rounded_rect_2d(w, h, r) {
    rr = min(r, w / 2, h / 2);
    hull() {
        translate([rr, rr]) circle(r = rr);
        translate([w - rr, rr]) circle(r = rr);
        translate([rr, h - rr]) circle(r = rr);
        translate([w - rr, h - rr]) circle(r = rr);
    }
}

module tach_slots_2d() {
    // PLACEHOLDER windows along the outer arch (0–9). Not OEM digit geometry.
    x0 = step_w;
    x1 = face_w - step_w;
    for (i = [0 : tach_slots - 1]) {
        t = i / (tach_slots - 1);
        u = (2 * t - 1) * 0.82;     // keep slots off the inset side walls
        p = arch_xy(u, x0, x1, face_h, spring_y);
        translate([p[0] - tach_slot_w / 2, p[1] - tach_slot_h - tach_slot_inset])
            rounded_rect_2d(tach_slot_w, tach_slot_h, 0.6);
    }
}

module lamp_window_2d() {
    translate([lamp_x, lamp_y])
        rounded_rect_2d(lamp_w, lamp_h, 1.2);
}

module button_caps_2d(extra = 0) {
    translate([rocker_x - extra, btn_y - extra])
        stadium_2d(rocker_w + 2 * extra, btn_h + 2 * extra);
    translate([sel_x - extra, btn_y - extra])
        stadium_2d(trip_w + 2 * extra, btn_h + 2 * extra);
    translate([trip_x - extra, btn_y - extra])
        stadium_2d(trip_w + 2 * extra, btn_h + 2 * extra);
}

module temp_bar_2d() {
    translate([temp_x, temp_y])
        rounded_rect_2d(temp_w, temp_h, 0.4);
}

module fuel_bar_2d() {
    translate([fuel_x, fuel_y])
        rounded_rect_2d(fuel_w, fuel_h, 0.4);
}

// Four PLACEHOLDER pins in the bottom bezel (not in the LCD). Fiction until measured.
function align_xy() = [
    [rocker_x + rocker_w + 4.0, 3.2],
    [sel_x - 4.0, 3.2],
    [rocker_x + rocker_w + 4.0, lcd_bot_y - 3.0],
    [sel_x - 4.0, lcd_bot_y - 3.0]
];

module align_holes_2d(d = align_hole_d) {
    for (p = align_xy())
        translate(p) circle(d = d);
}

function stem_xy() = [
    [rocker_x + rocker_w * 0.28, btn_y + btn_h / 2],
    [rocker_x + rocker_w * 0.72, btn_y + btn_h / 2],
    [sel_x + trip_w / 2, btn_y + btn_h / 2],
    [trip_x + trip_w / 2, btn_y + btn_h / 2]
];
