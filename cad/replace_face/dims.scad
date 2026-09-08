// =============================================================================
// PLACEHOLDER dimensions — Option 1 replace-face stack
// =============================================================================
// ESTIMATED millimetres from refs/flat/DIMENSIONS.md (170 × 72.3, 2.35:1).
// Face lock (#12): horizontal TEMP left / FUEL right flanking the speedo.
// Callipers are UNKNOWN. Every critical size is a guess until the OEM face
// and cluster bay are measured. This is NOT a verified AP1 drop-in.
//
// Origin (OpenSCAD): bottom-left of the module bounding box, Z toward driver.
// DIMENSIONS.md / pygame use top-left percentages — convert with y_from_top().
// =============================================================================

$fn = 48;
eps = 0.08;

// --- locked flat elevation (ESTIMATED mm from DIMENSIONS.md) ----------------
face_w = 170.0;             // ESTIMATED — TODO measure OEM face width
face_h = 72.3;              // ESTIMATED — 170 / 2.35; TODO measure height
face_aspect = 2.35;         // lock; do not invent a new family

step_w_pct = 0.044;         // rectangular side-notch depth
notch_top_pct = 0.58;       // from module top (OEM lock)
notch_bot_pct = 0.72;
arch_rise_pct = 0.28;       // y% = 28 * u² from the module top
arch_steps = 40;

lcd_inset_x_pct = 0.010;    // extra inset inside the notch
lcd_top_pct = 0.055;
lcd_bottom_pct = 0.76;      // LCD fills to the lamp strip (not under TEMP/FUEL)
lcd_spring_inset_pct = 0.02;
lcd_frame_mm = 1.0;         // PLACEHOLDER — keeps the mask one piece (see outline)

// AP1 lock (#12 / refs/flat/DIMENSIONS.md): horizontal bars flanking the
// speedo. NOT the old bottom-bar (y=72%) and NOT a vertical side stack.
temp_x_pct = 0.080;         // C→H left of speedo
temp_y_pct = 0.505;
fuel_x_pct = 0.760;         // E→F right of speedo
fuel_y_pct = 0.505;
bar_w_pct = 0.160;
bar_h_pct = 0.012;          // thin horizontal ticks (TEMP has 6)
temp_segs = 6;              // OEM AP1 coolant ticks — LCD-drawn, not a mask cut

speed_x_pct = 0.50;
speed_y_pct = 0.40;

lamp_y_pct = 0.805;         // hardware-strip centre-line
bezel_h_pct = 0.175;
lamp_w_pct = 0.50;          // PLACEHOLDER — telltale pack not callipered
lamp_h_from_bezel = 0.58;

btn_pad_x_pct = 0.018;
rocker_w_pct = 0.092;
trip_w_pct = 0.062;
btn_h_from_bezel = 0.48;
sel_gap_mm = 1.0;           // PLACEHOLDER (UI uses ~10 px on a 1920 canvas)

tach_slots = 10;            // 0..9 placeholder windows
tach_slot_w = 4.2;          // PLACEHOLDER mm
tach_slot_h = 5.5;          // PLACEHOLDER mm
tach_slot_inset = 3.2;      // PLACEHOLDER — inward from outer arch

// --- stack thicknesses (ALL PLACEHOLDER / TODO measure) ---------------------
face_t = 2.0;               // PLACEHOLDER acrylic / printed mask
tray_h = 12.0;              // PLACEHOLDER overall backlight tray
floor_t = 1.6;              // PLACEHOLDER backscreen floor
diffuser_t = 1.2;           // PLACEHOLDER opal sheet (bought, not printed)
wall = 2.0;                 // PLACEHOLDER tray wall
face_pocket_clear = 0.35;   // PLACEHOLDER slip around dropped-in face
lcd_pocket_clear = 0.40;    // PLACEHOLDER
cable_w = 16.0;             // PLACEHOLDER — FPC / tail location UNKNOWN
cable_h = 4.0;              // PLACEHOLDER

align_pin_d = 2.0;          // PLACEHOLDER — holes only; no printed bosses
align_hole_d = 2.3;         // PLACEHOLDER — do not drill the bay from this
align_pin_h = 2.6;          // PLACEHOLDER — unused until a pin is measured
align_boss_d = 4.4;         // PLACEHOLDER — unused (web/tray stay separate)

button_clear = 0.40;        // PLACEHOLDER hole oversize
button_cap_t = 2.4;         // PLACEHOLDER proud cap
button_flange_t = 1.2;      // PLACEHOLDER retention flange
button_flange_extra = 1.6;  // PLACEHOLDER radial flange beyond cap
button_stem_d = 3.0;        // PLACEHOLDER — switch model UNKNOWN
button_stem_h = 5.0;        // PLACEHOLDER — travel / switch height UNKNOWN
rocker_groove_w = 0.80;
rocker_groove_d = 1.10;

stem_well_d = 6.0;          // PLACEHOLDER switch well in the tray
stem_well_h = 7.0;          // PLACEHOLDER

// --- derived (still ESTIMATED; inherit the TODOs above) ---------------------
step_w = face_w * step_w_pct;
arch_rise = face_h * arch_rise_pct;
spring_y = face_h * (1 - arch_rise_pct);
notch_top_y = face_h * (1 - notch_top_pct);
notch_bot_y = face_h * (1 - notch_bot_pct);

lcd_x = step_w + face_w * lcd_inset_x_pct;
lcd_w = face_w - 2 * step_w - 2 * face_w * lcd_inset_x_pct;
lcd_peak_y = face_h * (1 - lcd_top_pct);
lcd_bot_y = face_h * (1 - lcd_bottom_pct);
lcd_spring_y = face_h * (1 - (arch_rise_pct - lcd_spring_inset_pct));

bezel_h = face_h * bezel_h_pct;
btn_h = bezel_h * btn_h_from_bezel;
btn_y_from_top = face_h * lamp_y_pct + (bezel_h - btn_h) / 2;
btn_y = face_h - btn_y_from_top - btn_h;

rocker_x = face_w * btn_pad_x_pct;
rocker_w = face_w * rocker_w_pct;
trip_w = face_w * trip_w_pct;
trip_x = face_w - face_w * btn_pad_x_pct - trip_w;
sel_x = trip_x - trip_w - sel_gap_mm;

lamp_w = face_w * lamp_w_pct;
lamp_h = bezel_h * lamp_h_from_bezel;
lamp_x = (face_w - lamp_w) / 2;
lamp_y_from_top = face_h * lamp_y_pct - lamp_h / 2;
lamp_y = face_h - lamp_y_from_top - lamp_h;

temp_x = face_w * temp_x_pct;
temp_w = face_w * bar_w_pct;
temp_h = face_h * bar_h_pct;
temp_y = face_h * (1 - temp_y_pct - bar_h_pct);

fuel_x = face_w * fuel_x_pct;
fuel_w = temp_w;
fuel_h = temp_h;
fuel_y = temp_y;

face_rebate_z = tray_h - face_t;
diffuser_z = floor_t;

function y_from_top(pct) = face_h * (1 - pct);

function arch_xy(u, x0, x1, y_peak, y_spring) =
    let (
        t = (u + 1) / 2,
        x = x0 + (x1 - x0) * t,
        y = y_peak - (y_peak - y_spring) * u * u
    )
    [x, y];
