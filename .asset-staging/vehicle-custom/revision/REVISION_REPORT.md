# Milestone 00C.1 Revision — Driver's-Eye Composition

**Status:** Ready for review  
**Original preserved:** `../beyond_school_cockpit_blockout.blend`  
**Revision:** `beyond_school_cockpit_blockout_revision.blend`  
**Blender:** 5.2.2 LTS  
**Scope:** Composition and blockout proportions only

## Files

- `beyond_school_cockpit_blockout_revision.blend`
- `driver_eye_A_balanced.png`
- `driver_eye_B_lower_road.png`
- `driver_eye_C_wide_context.png`
- `cockpit_overall.png`

The original Stage 1 Blender file and original render remain unchanged in the parent directory.

## Diagnosis of the original obstruction

The original render was not caused by a single camera error:

1. The eye marker was close to the steering wheel, producing a cramped view.
2. The upper dashboard pad and shell occupied too much vertical screen space.
3. The steering wheel sat high relative to the dashboard and visually merged into the obstruction.
4. The driver-side mirror was too far outward and low to read immediately.
5. The hazard switch was separate, but its original low placement reduced visual legibility.

The revision therefore changes both geometry and camera composition. It does not solve the problem by moving the camera arbitrarily.

## Revision changes

### Geometry

- Lowered `DASH_Shell` by 0.070 m.
- Lowered `DASH_UpperPad` by 0.080 m.
- Lowered `DASH_InstrumentBinnacle` by 0.060 m.
- Lowered `DASH_InstrumentCluster` by 0.040 m.
- Moved `STEERING_ROOT` rearward by 0.040 m and downward by 0.035 m.
- Moved the driver mirror inward by 0.080 m and upward by 0.040 m.
- Raised the separate `BTN_HazardSwitch` and `MARKER_HazardSwitch` by 0.035 m.

These are temporary blockout adjustments and must be rechecked when final dashboard surfacing is created.

### Camera variants

All renders are 1280 × 720 PNGs.

| Variant | Eye position (m) | Aim point (m) | Lens | Purpose |
|---|---|---|---:|---|
| A — Balanced | `(-0.620, -0.455, 1.310)` | `(2.800, -0.180, 1.390)` | 27 mm | Best balance of wheel, cluster, mirror, hazard and road |
| B — Lower road | `(-0.560, -0.455, 1.270)` | `(3.000, -0.160, 1.470)` | 26 mm | Maximizes forward road/horizon clearance |
| C — Wide context | `(-0.720, -0.455, 1.330)` | `(3.200, -0.120, 1.420)` | 24 mm | Shows more windshield frame and cockpit context |

The overall view uses:

- Position: `(2.900, -4.500, 2.400)` m
- Aim: `(0.300, 0.000, 1.000)` m
- Lens: 42 mm

## Render assessment

### Variant A — Balanced

Recommended composition for review. The steering wheel is clearly on the negative-Y driver side, the instrument cluster sits behind it, the road/horizon is visible above the dash, and the driver mirror and red hazard switch are immediately legible.

The dashboard still occupies the lower portion of the frame, as expected for a cockpit view, but it no longer eliminates the forward view.

### Variant B — Lower road

Provides the clearest forward road and horizon area and the least dashboard obstruction. The steering wheel and cluster remain readable, but the view is slightly less immersive as a seated cockpit composition.

Useful as a benchmark for the minimum acceptable forward visibility.

### Variant C — Wide context

Shows the most windshield frame and surrounding cockpit context. The wheel, hazard switch and mirror remain visible, but the scene reads more like a wide diagnostic camera than a final first-person view.

Useful for checking spatial layout, not recommended as the primary production camera.

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| Convincing seated driver's viewpoint | **PASS for blockout** | All three variants use a rearward eye position behind the steering wheel; no camera intersection is visible |
| Useful windshield and road view | **PASS for blockout** | Variants A–C show a clear blue horizon and road opening above the dashboard |
| Steering wheel clearly positioned | **PASS** | Wheel remains on negative-Y driver side and is unobstructed enough to read |
| Instrument cluster aligned behind wheel | **PASS** | Cluster/binnacle are centred behind the wheel in all variants |
| Driver-side mirror naturally visible | **PASS for blockout** | Mirror is visible at right side of each forward render after inward/upward adjustment |
| Hazard switch separate and identifiable | **PASS** | Red `BTN_HazardSwitch` remains an independent mesh and is visible left of the cluster |
| Human-scale proportions | **PASS provisionally** | Seat, wheel, dash and eye marker retain metre-scale dimensions; final ergonomic review remains required |
| No camera intersections | **PASS** | Reproduced renders show no clipping through dashboard, wheel, roof or A-pillars |

## Recommended composition

Use **Variant A — Balanced** as the current review candidate:

```text
MARKER_DriverEye / CAM_REV_A_balanced
Position: (-0.620, -0.455, 1.310) m
Aim:      ( 2.800, -0.180, 1.390) m
Lens:     27 mm
```

Variant B should remain as a forward-visibility fallback. Variant C should remain as a spatial-layout diagnostic.

## Limitations

- This remains temporary blockout geometry, not final photorealistic modelling.
- The windshield is still an opening marker; final glass is deferred.
- The road and horizon are diagnostic placeholders, not the approved highway environment.
- Mirror reflection behaviour is not validated.
- Hazard interaction, lamp synchronization, and RealityKit/USDZ export are not validated.
- The current render proves composition only; it does not prove final visual quality.

## Review gate

Do not proceed to detailed dashboard modelling until Variant A or an explicitly selected alternative is approved. Review the four renders together, especially:

1. Forward road clearance.
2. Driver-side mirror legibility.
3. Hazard-switch reach and visibility.
4. Steering-wheel and instrument-cluster relationship.
5. Eye height and seated-driver realism.
