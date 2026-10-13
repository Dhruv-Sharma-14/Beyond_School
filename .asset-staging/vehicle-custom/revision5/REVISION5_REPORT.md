# Milestone 00C.1 Revision 5 — Steering Wheel and Forward Composition

**Status:** Ready for review  
**Source preserved:** `../revision4/beyond_school_cockpit_blockout_revision4.blend`  
**Revision file:** `beyond_school_cockpit_blockout_revision5.blend`  
**Scope:** Locked MID driver's-eye composition and steering-assembly correction

## Deliverables

- `beyond_school_cockpit_blockout_revision5.blend`
- `driver_eye_revision5_mid.png`
- `cockpit_overall_revision5.png`
- `create_steering_forward.py`

The original blockout and Revisions 1–4 are unchanged.

## Locked camera

Revision 5 uses the existing MID camera and does not create another eye-height series:

```text
Camera:   REV4_Camera_MID
Position: (-0.620, -0.455, 1.290) m
Aim:      (6.000, -1.300, -0.700) m
Lens:     24 mm
Marker:   MARKER_DriverEye = (-0.620, -0.455, 1.290) m
```

The eye height remains exactly `1.290 m`. The aim is lowered and extended only to bring the existing road corridor into the useful windshield area.

## Steering inspection and correction

Revision 4 was inspected before editing. Its torus rim was continuous, but its three inherited spoke objects were vertical cylinders whose world-space endpoints did not form connected hub-to-rim members. Revision 5 removes those defective spoke objects and creates three planar rectangular bars:

- `STEERING_ROOT` at `(0.420, -0.455, 1.080) m`
- `STEERING_Wheel` — existing continuous rim
- `STEERING_Hub` — existing hub, concentric with the pivot
- `REV5_SteeringSpoke_00..02` — separate bars spanning the hub perimeter to the rim inner perimeter
- `STEERING_Column` — retained forward-directed connection toward the dashboard

The wheel remains in the vertical Y/Z plane, with its normal along +X toward the seated driver. The root is the stable future steering-interaction pivot.

## Forward composition correction

The temporary dashboard shell and upper pad are lowered by an additional `0.055 m` and `0.035 m` respectively. This is a blockout-only adjustment; the instrument cluster, wheel, mirror and hazard switch remain in their Revision 4 relationships. No lane markings were relocated.

## Visual validation

The driver's-eye render must show:

- A complete rim with visibly connected spokes and hub.
- The steering column extending toward the dashboard.
- Road surface and lane corridor through the windshield.
- Shoulder and `HIGHWAY ASSISTANCE` sign.
- Driver-side mirror and separate hazard switch.

## Render findings

| Criterion | Result | Evidence |
|---|---|---|
| MID eye height remains locked at `1.290 m` | **PASS** | `REV4_Camera_MID` and `MARKER_DriverEye` both remain at `(-0.620, -0.455, 1.290)` |
| Rim is continuous | **PASS for blockout** | Existing torus rim is retained and verified as a continuous mesh |
| Spokes connect hub to rim | **PASS for blockout** | `REV5_SteeringSpoke_00..02` are planar bars spanning the hub perimeter to the rim inner perimeter |
| Hub and pivot are coherent | **PASS** | `STEERING_ROOT`, `STEERING_Wheel`, and `STEERING_Hub` share `(0.420, -0.455, 1.080)` world-space center |
| Column points toward dashboard | **PASS for blockout** | `STEERING_Column` remains forward-directed toward `+X`; it does not project toward the driver |
| Wheel/dashboard intersection | **PASS provisionally** | Driver-eye render shows no obvious wheel penetration; the lowered temporary shell/pad preserve clearance |
| Road corridor is useful | **PASS for blockout** | Driver-lane-aligned MID render shows the road surface, repeated lane markings and shoulder through the forward opening |
| Shoulder and assistance sign remain visible | **PASS** | Right shoulder and `HIGHWAY ASSISTANCE` board remain readable |
| Mirror and hazard switch remain present | **PASS for blockout** | Driver-side mirror is visible at right; separate red hazard switch remains at left |
| Camera clipping | **PASS provisionally** | Render completed without visible camera intersection |

## Limitations

This is still temporary blockout geometry. The dashboard proportions and temporary controls are not production quality, the road is a simple diagnostic slab, and the steering rim/spokes remain simplified. No detailed dashboard modelling, traffic, driving physics, tyre repair, Reality Composer Pro import, USDZ export, or Apple Vision Pro validation was performed.
