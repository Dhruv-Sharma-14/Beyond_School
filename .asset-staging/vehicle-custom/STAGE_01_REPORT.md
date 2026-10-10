# Stage 01 Report — Cockpit Blockout

**Status:** Generated for review  
**Stage:** Milestone 00C.1, Stage 0 reference sheet and Stage 1 cockpit blockout  
**Tool:** Blender 5.2.2 LTS  
**Source script:** `create_blockout.py`

## Deliverables

- `beyond_school_cockpit_blockout.blend`
- `driver_eye_blockout.png`
- `REFERENCE_AND_MEASUREMENTS.md`
- `STAGE_01_REPORT.md`

The Blender project and render are contained entirely in `.asset-staging/vehicle-custom/`.

## Scene contents

The editable scene contains temporary but proportioned blockout geometry for:

- Cabin floor.
- Transmission tunnel.
- Driver and passenger seats.
- Dashboard shell and upper pad.
- Right-hand-drive steering root, column, wheel and hub.
- Instrument binnacle and cluster.
- Centre stack and infotainment placeholder.
- Separate hazard switch and icon geometry.
- Driver and passenger exterior mirror assemblies.
- Windshield opening marker and A-pillars.
- Roof header.
- Driver-eye, hazard-switch, and driver-mirror markers.
- Temporary road plane, lane marking, and horizon backdrop.
- Basic daylight area lights.

No detailed exterior, trunk, wheel assemblies, traffic, production scene, Swift source, Xcode settings, or Reality Composer Pro content was created.

## Coordinate orientation

- `+X`: forward.
- `-X`: rearward.
- `-Y`: driver side.
- `+Y`: passenger side.
- `+Z`: up.
- Origin: wheelbase centre at ground level.
- Units: metres.

The scene root is `VEHICLE_ROOT`. Its custom property records the coordinate convention and stage status.

## Stable object hierarchy

Important runtime-facing names include:

```text
VEHICLE_ROOT
├── SEAT_Driver
│   ├── SEAT_Driver_Cushion
│   ├── SEAT_Driver_Backrest
│   └── SEAT_Driver_Headrest
├── SEAT_Passenger
├── STEERING_ROOT
│   ├── STEERING_Column
│   ├── STEERING_Wheel
│   └── STEERING_Hub
├── DASH_Shell
├── DASH_UpperPad
├── DASH_InstrumentBinnacle
├── DASH_InstrumentCluster
├── CONSOLE_CentreStack
├── CONSOLE_InfotainmentScreen
├── BTN_HazardSwitch
├── MIRROR_Driver
├── MIRROR_Passenger
├── GLASS_WindshieldOpening
├── A_Pillar_Driver
├── A_Pillar_Passenger
├── MARKER_DriverEye
├── MARKER_HazardSwitch
└── MARKER_Mirror_Driver
```

Interactive objects have useful origins and custom properties where appropriate. The hazard switch is a separate mesh with `interactive = True` and `function = Hazard light toggle`.

## Driver-eye validation

The diagnostic camera is `CAM_DriverEye`. It copies the transform of `MARKER_DriverEye` and aims toward the forward road/horizon. The current marker is:

```text
X = -0.350 m
Y = -0.455 m
Z =  1.285 m
```

This is rearward of the original blueprint estimate because the first composition placed the camera too close to the steering wheel. The adjusted position gives a more plausible seated-driver distance.

The diagnostic render demonstrates:

- Steering wheel on the negative-Y driver side.
- Instrument cluster behind the wheel.
- Driver-side mirror geometry in the left side of the forward view.
- A separate red hazard-switch block on the centre stack.
- A road plane and blue daylight horizon through the open windshield.
- A-pillars and roof header framing the forward view.

The render is intentionally a blockout, not a photorealistic vehicle benchmark. Temporary materials are restrained and geometry is simple.

## Acceptance-test results

| Gate | Result | Notes |
|---|---|---|
| Right-hand-drive arrangement | **PASS for blockout** | Driver seat, steering root, wheel, cluster, and driver mirror use negative Y |
| Seated driver-eye relationship | **PASS for blockout** | Marker was moved rearward after initial composition check |
| Clear windshield/road view | **PASS for blockout** | Windshield is an opening at this stage; temporary road and horizon are visible |
| Natural mirror placement | **PASS for blockout** | Driver-side mirror assembly is placed on negative Y and included in view framing |
| Separate hazard switch | **PASS** | `BTN_HazardSwitch` is an independent mesh with a separate icon child |
| Coherent scale/transforms | **PASS** | Metric units, metre dimensions, applied primitive scales, stable object origins |
| Reproducible `.blend` and render | **PASS** | Script regenerates the `.blend` and `driver_eye_blockout.png` with Blender 5.2.2 |

## Limitations and required review

- The scene is a temporary cockpit blockout and must not be presented as final realism.
- The windshield is represented by an opening marker; final glass, thickness, tint, and reflection behaviour are deferred.
- Seats, dashboard, mirrors, and controls require detailed surfacing and production materials in later stages.
- The temporary horizon is not a highway environment and contains no traffic, signs, barriers, or lighting integration.
- Human-scale validation is visual and dimensional, not a regulatory ergonomic certification.
- RealityKit/USDZ export has not been performed in this stage.
- Reality Composer Pro and Apple Vision Pro hardware were not available for validation.
- The chosen driver-eye position and hazard-switch reach require review before detailed modelling.

## Review decision requested

Review the blockout composition and approve or reject progression to dashboard detail. No detailed modelling or production integration should begin until the following are accepted:

1. Driver-eye marker position.
2. Dashboard height and steering-wheel relationship.
3. Mirror placement and sightline.
4. Hazard-switch placement.
5. Proposed dimensions and coordinate convention.
