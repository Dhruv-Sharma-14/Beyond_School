# Beyond School — Stage 6 USDZ Export Validation

## Deliverables

Stage 6 is derived from the read-only Stage 5 source `../stage5/beyond_school_stage5_complete_vehicle.blend`. The source SHA-1 remains `61acbddb413f58bb71047494c58f7e0b9825dbf1`.

| File | Size |
|---|---:|
| `create_stage6_usdz_export.py` | 15.0 KB |
| `beyond_school_stage6_export_ready.blend` | 3.49 MB |
| `beyond_school_vehicle_scene.usdz` | 3.11 MB |
| `driver_eye_stage6.png` | 1.42 MB |
| `flat_tyre_hub_unobstructed_stage6.png` | 1.13 MB |
| `repair_in_progress_stage6_clear.png` | 1.17 MB |
| `usdz_roundtrip_preview_stage6.png` | 0.87 MB |

All PNGs are 1280x720.

## Stage 6 implementation

- Replaced each full-length lower sill with three segments whose gaps span the requested wheel-arch intervals: rear `-1.67..-0.93 m`, centre `-0.93..+0.93 m`, and front `+0.93..+1.67 m`. Dark liner guides remain at each wheel centre with a 0.370 m clearance radius.
- Reconciled `WHEEL_RL_FlatTarget` to `(-1.300, +0.7675, 0.320) m`, matching the Stage 5 hub/stud/lug side.
- Added eight low-cost rotor ventilation details, a metallic gold caliper finish, and bevel modifiers to the jack/wrench meshes.
- Applied packed 1024 asphalt diffuse, ARM, and relief resources to the road material and added six textured concrete barrier blocks along the roadside.
- Kept cameras and lights out of the USD export; `MARKER_DriverEye` remains an exported transform.

## Validation

- Final blend: 426 objects, 49,674 evaluated vertices, 98,024 evaluated triangles. The evaluated total is above the earlier Stage 5 raw-mesh budget because inherited bevel modifiers are included; USDZ size remains below the required 8 MB limit.
- All 426 objects have `hide_render=False` and `hide_viewport=False`; no render used mesh hiding.
- `REV4_Camera_MID` / `MARKER_DriverEye` remains `(-0.620, -0.455, 1.290) m`.
- `TRUNK_Lid_Pivot` is reset to zero rotation before save/export. The diagnostic tyre, jack, and wrench transforms are also reset.
- All requested interactive prim names, including `MARKER_DriverEye`, steering/control pivots, wheel/hub/tool roots, lug pivots, `LAMP_Hazard_*`, `GLASS_Windshield`, and `DOOR_DriverRight_Glass`, are present in the authored USD hierarchy, verified with `usdcat`; Blender's re-import view omits several mesh prims as object instances, so the report does not mistake that importer limitation for USD name loss.
- `/usr/bin/usdchecker` passed with no errors after the road relief map was kept as a packed, non-connected resource and the export used USD-safe preview materials.
- USDZ contains `cluster_stage3_1024x512.png`, `infotainment_stage3_1024x512.png`, `clean_asphalt_diff_1024.jpg`, `clean_asphalt_arm_1024.jpg`, and `clean_asphalt_relief_1024.jpg`.

## Visual self-critique

- `driver_eye_stage6.png`: the cockpit, textured road surface, and barrier line read clearly, but this remains a benchmark environment rather than a photoreal highway.
- `flat_tyre_hub_unobstructed_stage6.png`: the segmented sill opens the kneeling sightline to the wheel/hub region; the rotor and caliper remain stylized and are not yet close-up photoreal mechanical detail; the inherited wheel geometry is still stylized and not production automotive topology.
- `repair_in_progress_stage6_clear.png`: the open trunk, displaced wheel target, jack and wrench staging are legible, but the pose is a diagnostic composition, not final interaction animation.
- `usdz_roundtrip_preview_stage6.png`: the fresh Blender import is renderable and preserves the scene appearance at a coarse level; Blender's USD importer does not expose every mesh prim as a one-to-one object, so RealityKit validation remains necessary.

## Readiness

Stage 6 is ready for native RealityKit/visionOS integration and USDZ inspection on-device. The remaining production risks are the inherited benchmark-level vehicle topology, evaluated triangle count, and the need to confirm material/transparency behavior on visionOS hardware.
