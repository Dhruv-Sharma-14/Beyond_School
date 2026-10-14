# Beyond School — Stage 2.1 Dashboard Geometry Refinement

**Status:** Ready for review  
**Source:** `../stage2/beyond_school_stage2_dashboard.blend`  
**Output:** `beyond_school_stage2_1_dashboard.blend`  
**Scope:** Visible dashboard, instrument, centre-stack, and console geometry refinement

## Deliverables

- `beyond_school_stage2_1_dashboard.blend`
- `driver_eye_stage2_1.png`
- `dashboard_controls_stage2_1_close.png`
- `cockpit_overall_stage2_1.png`
- `create_stage2_1_refinement.py`

The original blockout, Revisions 1–5, and the Stage 2 source remain unchanged.

## Geometry changes

- Replaced the broad Stage 2 dashboard shell and fascia with overlapping, radiused upper/lower shells, a recessed contour inset, and a continuous accent rail.
- Rebuilt the instrument binnacle as a deeper hood with a recessed bezel, dark replaceable display surface, and four small dial/tick details instead of two white discs.
- Integrated the centre stack into the dashboard with a softened surround, recessed neutral infotainment surface, restrained `READY` startup mark, separate vents and directional slats.
- Rebuilt the climate-control panel and knobs as a coherent horizontal control bank.
- Reshaped the centre tunnel support beneath the gear selector and parking brake.
- Retained glovebox seam, steering-column shroud, lower footwell trim, and pedal surfaces with softened transitions.
- Final PBR materials, instrument graphics, and lighting remain deferred to Stage 3.

## Preserved objects and interaction names

The following remain independently addressable:

- `BTN_HazardSwitch`
- `BTN_HazardSwitch_Cap`
- `BTN_HazardSwitch_Icon`
- `BTN_HazardSwitch_Pivot`
- `CTRL_ClimateKnob_00..02`
- `CONSOLE_GearSelector`
- `CONSOLE_GearSelector_Pivot`
- `CTRL_ParkingBrake`
- `CTRL_ParkingBrake_Pivot`

Hazard, climate, gear, and parking-brake controls carry interaction metadata and pivot coordinates. The gear selector remains marked `manual_or_automatic`; the parking brake remains marked `manual_handbrake_or_electronic_switch`.

## Preserved scene and camera

- `REV4_Camera_MID` remains the approved driver's-eye camera at its existing transform and eye height.
- Exact camera transform: location `(-0.620, -0.455, 1.290) m`, lens `24 mm`; `MARKER_DriverEye` remains coincident at `(-0.620, -0.455, 1.290) m`.
- `STEERING_ROOT`, `STEERING_Wheel`, `STEERING_Hub`, `STEERING_Column`, seats, mirrors, windshield opening, road, lane markings, shoulder, and `HIGHWAY ASSISTANCE` sign are preserved from Stage 2.
- No dashboard lowering or eye-height change was used to force the road view.
- Coordinate system remains metres: `+X` forward, `-Y` driver side, `+Y` passenger side, `+Z` up.

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| Dashboard no longer reads as stacked cuboids | **PASS for blockout** | Radiused overlapping shells, fascia inset, accent rail, and integrated stack visible in the close-up and driver's-eye render |
| Instrument cluster integrated and aligned | **PASS for blockout** | Recessed hood/bezel and replaceable dial surfaces remain behind the preserved steering wheel |
| Centre stack, vents, screen and climate controls coherent | **PASS for blockout** | Softened centre-stack surround, recessed screen, separate vents/slats, and climate bank visible |
| Gear selector and parking brake supported | **PASS for blockout** | Both controls sit on the reshaped centre tunnel with stable pivots |
| Hazard switch physical and independently addressable | **PASS** | Separate cap, icon, pivot, and parent control are present and visible |
| Forward road view remains usable | **PASS provisionally** | Approved MID camera is unchanged; road, shoulder, mirror, and sign remain visible |
| Blender file reopens and required objects resolve | **PASS** | Blender 5.2.2 headless reopen confirms names, pivots, metric units, and 1280×720 settings |

Headless validation confirmed no duplicate required interaction names. The visible control world positions are hazard `(0.430, 0.000, 1.075)`, climate knobs `(0.447, -0.150/0.000/0.150, 0.870)`, gear selector `(0.100, 0.080, 0.660)` over pivot `(0.100, 0.080, 0.550)`, and parking brake `(-0.180, 0.170, 0.560)` over pivot `(-0.180, 0.170, 0.470)`.

## Remaining limitations

This remains a geometry-stage diagnostic. Final automotive materials, UVs, PBR textures, instrument graphics, control animations, vent mechanics, climate logic, gear-state logic, Reality Composer Pro/USDZ import, and Apple Vision Pro profiling are deferred to later work.
