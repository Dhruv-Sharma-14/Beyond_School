# Beyond School — Stage 4 Exterior RHD Sedan Body

**Status:** Ready for review  
**Source:** `../stage3/beyond_school_stage3_interior_pbr.blend`  
**Output:** `beyond_school_stage4_exterior_body.blend`

## Deliverables and sizes

| File | Size |
|---|---:|
| `create_stage4_exterior.py` | 17.8 KB |
| `beyond_school_stage4_exterior_body.blend` | 311.4 KB |
| `driver_eye_stage4.png` | 1225.8 KB |
| `dashboard_controls_stage4_close.png` | 1143.6 KB |
| `exterior_front_right_stage4.png` | 1123.6 KB |
| `exterior_rear_left_stage4.png` | 1186.2 KB |

## Blueprint dimensions and hierarchy

- Coordinate convention preserved: `+X` forward, `-Y` RHD driver side, `+Z` up; origin at wheelbase centre.
- Target exterior envelope: **4.430 × 1.765 × 1.485 m** excluding mirrors; mirror envelope approximately **2.000 m**.
- Wheelbase: **2.600 m**; front axle `X=+1.300 m`; rear axle `X=-1.300 m`.
- Tracks: front `Y=±0.765 m`; rear `Y=±0.7675 m`; wheel centres `Z=0.320 m`; ground clearance `0.165 m`; tyre OD `0.640 m`.
- Door pivot: `DOOR_DriverRight_Pivot` at `(0.520, -0.880, 0.680) m`.
- Trunk pivot: `TRUNK_Lid_Pivot` at `(-1.550, 0.000, 1.060) m`.
- Required wheel assemblies: `WHEEL_FL`, `WHEEL_FR`, `WHEEL_RL_FlatTarget`, `WHEEL_RR`.
- Required lamp assemblies and amber objects: `LAMP_Hazard_FL/FR/RL/RR/Side_R/Side_L`.

## Current implementation

- Added a panel-based compact sedan exterior with lower shell, hood, roof, bumpers, pillars, door panels, glazing, trunk lid, trunk well cavity, floor mat, mirrors, lamps, and four low-poly wheel assemblies.
- Added openable driver-door hierarchy under `DOOR_DriverRight_Pivot` and openable trunk hierarchy under `TRUNK_Lid_Pivot`.
- Added USDZ-safe Principled materials for pearl body paint, dark trim, tinted glazing, mirror glass, hazard amber, headlamps, taillamps, tyres, and alloy wheels.
- Fixed Stage 3 cluster layout for oblique viewing: smaller outer dial rings centered at `Y=-0.535/+/-` and `Y=-0.375`, with a central warning panel and text between them. The warning panel is kept at a controlled `1.5 mm` diagnostic offset relative to the cluster-facing bezel plane.
- Preserved Stage 3 interior names, pivots, materials, metric units, and `REV4_Camera_MID`.

## Validation

- Blender 5.2.2 headless generation: **PASS**.
- Required scene remains metric with scale length 1.0: **PASS**.
- Active camera after save: `REV4_Camera_MID`: **PASS**.
- Required door, trunk, lamp, mirror, wheel, and Stage 3 interaction names: **PASS**.
- Duplicate required names: **none**.
- Stage 4 mesh totals: **10,732 vertices / 20,524 triangles**; triangle budget under 35,000: **True**.
- Preserved camera eye position: `(-0.620, -0.455, 1.290) m`.
- Sightline clearance remains diagnostic: camera-to-upper-shell vertical clearance documented by Stage 3 as `0.284 m`; the exterior body is panel-based to avoid filling the cabin view.
- All renders: **1280×720**.

## Visual inspection and self-critique

- Driver-eye render: cluster warning panel is centered between the dial rings, hazard switch remains clear, and the road/mirror/sign relationship is preserved. Exterior roof/side panels intentionally remain outside the main forward sightline.
- Dashboard close-up: the warning panel and outer dial separation read more cleanly than Stage 3 from the oblique camera, though the generated text remains diagnostic-scale.
- Front-right exterior: shows the pearl-silver body, right-hand driver side, door, mirror, front hazard lamps, headlamps, and cockpit through the tinted glazing.
- Rear-left exterior: shows the trunk/boot, rear lamps, rear-left wheel position, and spare-well-ready rear volume.
- Remaining limitations: exterior surfaces are still a low-detail benchmark body, door/trunk opening animations are not authored, lamp blinking is not wired to RealityKit state, and no USDZ export or hardware profiling has been performed.

## Recommendation

Stage 4 is ready for review. Stage 5 may proceed after approval to build the removable rear-left flat tyre, lug nuts, spare tyre, scissor jack, and lug wrench.
