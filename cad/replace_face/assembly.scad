// =============================================================================
// PLACEHOLDER — stacked preview (Option 1 replace-face)
// =============================================================================
// F5 preview. Explode is millimetres of air between layers — not a fit claim.
// Exporting this STL is optional; the three part STLs are the printables.
// =============================================================================

include <parts.scad>

explode = 14;   // set 0 for a closed stack
assembly(explode);
