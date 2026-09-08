// =============================================================================
// PLACEHOLDER — stacked preview (Option 1 replace-face)
// =============================================================================
// F5 preview only — do not export a combined STL (multi-body, poor remesh).
// Explode is millimetres of air between layers — not a fit claim.
// =============================================================================

include <parts.scad>

explode = 14;   // set 0 for a closed stack
assembly(explode);
