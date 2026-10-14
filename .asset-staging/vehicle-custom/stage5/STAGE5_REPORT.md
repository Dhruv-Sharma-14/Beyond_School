# Beyond School — Stage 5 Mechanical Flat-Tyre System and Toolkit

**Status:** Generated, rendered, and validated
**Source:** `../stage4_1/beyond_school_stage4_1_exterior_refined.blend`
**Output:** `beyond_school_stage5_complete_vehicle.blend`

## Files and sizes

| File | Size |
|---|---:|
| `create_stage5_tyre_tools_realism.py` | 27.83 KB |
| `beyond_school_stage5_complete_vehicle.blend` | 364.3 KB |
| `driver_eye_stage5.png` | 1451.8 KB |
| `exterior_front_right_stage5.png` | 1163.6 KB |
| `flat_tyre_closeup_stage5.png` | 1187.33 KB |
| `trunk_toolkit_closeup_stage5.png` | 1252.0 KB |
| `repair_in_progress_stage5_diag.png` | 1248.3 KB |

## New object/pivot table

- `TYRE_RL_DeflatedCarcass`; `HUB_RL_Assembly` with brake disc, caliper, five studs, five lug nuts and nut pivots.
- `JACK_Point_RL` at `(-0.980, 0.810, 0.165) m` and marker.
- `WHEEL_Spare`, `WHEEL_Spare_Pivot`, `TRUNK_SpareClamp`.
- `TOOL_ScissorJack_Root`, arms, lead screw, saddle and crank eye.
- `TOOL_LugWrench_Root`, shaft, socket head and spin pivot.
- `TOOL_WarningTriangle_Root`, base and reflector.
- `TRUNK_Lid_Pivot` opens on local Y and is saved closed.

## Validation

- Stage 4.1 SHA-1: `d65498914a9f2aa169a90d9793a5f56a95dfc1bc`.
- Metric units, active `REV4_Camera_MID`, prior names/pivots preserved.
- Zero hiding asserted for every render.
- Diagnostic trunk/tyre/tool poses reset before save.
- Mesh totals: **14,084 vertices / 26,956 triangles**; `<34,000`: **True**.
- All five renders: 1280×720.

## Visual self-critique

- Driver-eye: cockpit, road and slimmer greenhouse remain visible; roadway texture remains benchmark-level.
- Front-right: paint highlights and slimmer greenhouse read better, but final automotive photorealism is not yet achieved.
- Flat-tyre: the deflated carcass and arch are visible, but the close camera is partially occluded by the sill/body rail; brake hardware and lug details are structurally present and need a later camera/surface polish pass for presentation quality.
- Trunk toolkit: open upward trunk exposes spare and tools; tool geometry is functional benchmark detail.
- Repair diagnostic: outward tyre offset and tool staging are visible, although the body rail still competes with the hub in the frame; this is diagnostic rather than final cinematography.

## Next milestone

Ready for review before Stage 6 USDZ export validation.
