# Beyond School — Stage 2 Dashboard Detailing and Control Separation

**Status:** Ready for review  
**Source:** `../revision5/beyond_school_cockpit_blockout_revision5.blend`  
**Output:** `beyond_school_stage2_dashboard.blend`  
**Scope:** Dashboard, centre stack, and interaction-control detailing only

## Deliverables

- `beyond_school_stage2_dashboard.blend`
- `driver_eye_stage2.png`
- `dashboard_controls_stage2_close.png`
- `cockpit_overall_stage2.png`
- `create_stage2_dashboard.py`

Previous revisions and the Revision 5 source are preserved unchanged.

## Preserved scene elements

The existing `STEERING_ROOT`, `STEERING_Wheel`, `STEERING_Hub`, `STEERING_Column`, `MARKER_DriverEye`, mirrors, seats, windshield opening, temporary road, lane markings, shoulder, and `HIGHWAY ASSISTANCE` sign remain in the Stage 2 derivative. The approved MID camera remains active at the end of generation.

Coordinate convention remains metric:

- `+X`: forward
- `-X`: rearward
- `-Y`: driver side
- `+Y`: passenger side
- `+Z`: upward

## New dashboard and control hierarchy

### Dashboard and visible trim

- `DASH_UpperShell`
- `DASH_LowerFascia`
- `DASH_AccentRail`
- `DASH_InstrumentBinnacle`
- `DASH_InstrumentClusterBezel`
- `DASH_InstrumentCluster`
- `DASH_ClusterDial_00`, `DASH_ClusterDial_01`
- `DASH_GloveboxDoor`, `DASH_GloveboxSeam`
- `STEERING_ColumnShroud`
- `FOOTWELL_DriverTrim`
- `PEDAL_00..02`

The former temporary dashboard objects are hidden only in the Stage 2 derivative. The replacement uses layered bevelled shells and separate trim surfaces rather than leaving large cuboids as the apparent finished design.

### Centre stack and controls

- `CONSOLE_CentreStack`
- `CONSOLE_InfotainmentFrame`
- `CONSOLE_InfotainmentScreen`
- `CONSOLE_InfotainmentMark`
- `CONSOLE_AirVent_00`, `CONSOLE_AirVent_01` and slot children
- `BTN_HazardSwitch`
- `BTN_HazardSwitch_Cap`
- `BTN_HazardSwitch_Icon`
- `BTN_HazardSwitch_Pivot`
- `CTRL_ClimatePanel`
- `CTRL_ClimateKnob_00..02`
- `CONSOLE_CentreTunnel`
- `CONSOLE_GearSelector`
- `CONSOLE_GearSelectorBase`
- `CONSOLE_GearSelector_Pivot`
- `CTRL_ParkingBrake`
- `CTRL_ParkingBrakeBase`
- `CTRL_ParkingBrake_Pivot`

The hazard cap, icon, pivot and parent control are independently addressable. Gear and parking-brake objects carry explicit variant metadata for future manual/automatic and mechanical/electronic configurations.

## Camera and renders

- `driver_eye_stage2.png` uses the existing `REV4_Camera_MID`; eye height and preferred driver's-eye relationship are unchanged.
- `dashboard_controls_stage2_close.png` is a close-up diagnostic view from `STAGE2_Camera_DashboardClose`.
- `cockpit_overall_stage2.png` is an external overall view showing both seats, dashboard, windshield frame, road corridor and sign.

All renders are 1280 × 720.

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| Dashboard reads as intentional automotive design | **PASS for blockout** | Layered upper shell, lower fascia, accent rail, binnacle, centre stack and glovebox seam are visible in Stage 2 renders |
| Steering wheel, column and cluster remain coherent | **PASS provisionally** | Existing Revision 5 steering assembly is preserved; new binnacle/bezel/dial surfaces are aligned behind it |
| Hazard switch independently addressable | **PASS** | Four named objects and explicit pivot metadata are present |
| Vents, screen, climate controls, gear selector and parking brake separate | **PASS** | Separate named meshes/pivots are present and visible in close-up/overall views |
| Forward road view remains usable | **PASS provisionally** | Driver-eye render uses the approved MID camera and preserves the existing road/sign composition |
| Mirror and driver's-eye relationship remain usable | **PASS provisionally** | Existing driver mirror and marker are preserved; render review required for final sign-off |
| Scene reopens and renders reproduce | **PASS** | Blender 5.2.2 generation and headless reopen validation completed |

## Unresolved issues

- Materials remain diagnostic and require Stage 3 PBR treatment.
- Instrument graphics are neutral placeholders.
- Air-vent adjustment animation, climate logic, gear-state logic, and parking-brake behavior are not implemented.
- Pedal geometry is a visible placeholder and requires ergonomic validation.
- No Reality Composer Pro/USDZ import or Apple Vision Pro profiling was performed.
