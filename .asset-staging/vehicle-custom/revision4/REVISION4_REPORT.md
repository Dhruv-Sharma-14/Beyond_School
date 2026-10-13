# Milestone 00C.1 Revision 4 — Driver Ergonomics and Steering Assembly

**Status:** Ready for review  
**Source preserved:** `../revision3/beyond_school_cockpit_blockout_revision3.blend`  
**Revision file:** `beyond_school_cockpit_blockout_revision4.blend`  
**Scope:** Ergonomic camera and temporary steering-assembly correction

## Deliverables

- `beyond_school_cockpit_blockout_revision4.blend`
- `driver_eye_revision4_low.png`
- `driver_eye_revision4_mid.png`
- `driver_eye_revision4_high.png`
- `cockpit_overall_revision4.png`
- `create_ergonomics.py`

The original blockout and Revisions 1–3 are unchanged.

## Eye-height test

Revision 3 used a `Z = 1.450 m` camera and marker to expose the road. That is outside the approved seated-driver design target. Revision 4 tests three heights measured from the vehicle ground plane:

| Variant | Eye/camera position (m) | Aim point (m) | Purpose |
|---|---:|---:|---|
| LOW | `(-0.620, -0.455, 1.250)` | `(4.800, -0.200, 0.020)` | Lower, more enveloped cockpit view; 24 mm lens |
| MID | `(-0.620, -0.455, 1.290)` | `(4.800, -0.200, 0.120)` | Balanced seated-driver composition; 24 mm lens |
| HIGH | `(-0.620, -0.455, 1.330)` | `(4.800, -0.200, 0.220)` | Maximum approved eye height and road visibility; 24 mm lens |

The preferred marker and active camera are restored to the MID variant after rendering. The driver-eye marker is never above `1.330 m`.

## Steering assembly correction

- `STEERING_ROOT` is centered at `(0.420, -0.455, 1.080) m`, matching the lowered wheel hub and providing a future rotation pivot.
- The existing rim and hub are preserved and explicitly supplemented with three separate spoke objects: `REV4_SteeringSpoke_00` through `REV4_SteeringSpoke_02`.
- The rim is reduced to approximately 86% of the previous blockout diameter to prevent near-field dominance.
- The steering column is rebuilt as `STEERING_Column` from `(0.420, -0.455, 1.080)` toward `(0.670, -0.455, 1.020)`, extending forward toward the dashboard rather than toward the driver.
- The wheel remains in the vertical Y/Z plane appropriate to a seated driver looking along +X.
- The instrument cluster remains behind and aligned with the wheel at the driver-side dashboard position.
- The temporary dashboard shell and upper pad are lowered a further `0.12 m` and `0.08 m` respectively in this revision so the road corridor is visible without raising the eye marker.

## Visual acceptance

Each driver's-eye render must visibly demonstrate:

- Road surface and lane markings through the windshield.
- Steering rim, hub and spokes.
- Instrument cluster behind the wheel.
- Driver-side mirror.
- Separate hazard switch.
- A seated-driver relationship without camera intersections.

### Variant recommendation

**MID is recommended** as the starting composition. LOW maximizes cockpit enclosure but gives the dashboard more visual weight. HIGH improves road visibility but approaches the upper ergonomic limit and risks making the driver feel too tall. MID is the best compromise for later detailed modelling, subject to visual review of the three renders.

## Render findings

| Criterion | Result | Evidence |
|---|---|---|
| Eye heights remain within `1.25–1.33 m` | **PASS** | LOW, MID and HIGH renders use `1.250`, `1.290` and `1.330 m` respectively |
| Steering wheel is complete and concentric with hub | **PASS for blockout** | Rim, hub and three explicit spokes are visible; saved origins coincide at `(0.420, -0.455, 1.080)` |
| Steering column points toward dashboard | **PASS for blockout** | Column runs forward from the hub toward `+X`, ending at `(0.670, -0.455, 1.020)` |
| Instrument cluster aligns behind wheel | **PASS for blockout** | Cluster remains centered on the driver-side dashboard behind the wheel |
| Road and lane markings remain visible | **PASS provisionally** | Road edge and repeated lane-marking segments remain visible through the windshield, primarily on the passenger-side forward corridor |
| Driver-side mirror remains visible | **PASS for blockout** | Mirror is visible in all three 24 mm driver's-eye renders |
| Hazard switch remains separate and reachable | **PASS for blockout** | Red `BTN_HazardSwitch` remains independently visible on the left side of each render |
| Camera avoids obvious clipping | **PASS provisionally** | All three renders complete without camera intersection; final visual review is still required |

## Validation performed

- Blender 5.2.2 LTS generated all four renders.
- The Revision 4 `.blend` was reopened headlessly.
- Required cockpit, road, sign, camera, steering, mirror and hazard objects were checked by name.
- Metric units and 1280×720 render settings were verified.
- The saved wheel and hub world-space translations were checked and both equal `(0.420, -0.455, 1.080)`.

## Limitations

This remains temporary blockout geometry. No detailed materials, traffic, driving physics, tyre-repair features, Reality Composer Pro import, USDZ export, or Apple Vision Pro validation was performed.
