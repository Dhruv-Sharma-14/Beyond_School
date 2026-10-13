# Milestone 00C.1 Revision 3 — Forward-View Correction

**Status:** Ready for review  
**Source preserved:** `../revision2/beyond_school_cockpit_blockout_revision2.blend`  
**Revision file:** `beyond_school_cockpit_blockout_revision3.blend`  
**Preferred camera:** `CAM_REV_A_balanced` with corrected aim  
**Scope:** Temporary forward-road composition test only

## Deliverables

- `beyond_school_cockpit_blockout_revision3.blend`
- `driver_eye_revision3_A_forward.png`
- `cockpit_overall_revision3_forward.png`
- `create_forward_view.py`

Original blockout, Revision 1, and Revision 2 remain unchanged.

## Diagnosis of Revision 2

Revision 2's actual driver-eye render was inspected rather than relying on its report:

- The dashboard and cockpit framing were readable.
- The assistance sign and road edge appeared at the far right.
- The road surface occupied too little of the forward view.
- Lane markings were clustered low and at the edge rather than forming a corridor.
- The primary cause was projection: Variant A's original aim point was above the road plane (`Z = 1.390 m`), producing a slightly rising forward view. At the driver's eye, the road therefore projected below the windshield opening.
- The road geometry was also spread laterally without being aligned to the camera's useful forward wedge.

## Revision 3 changes

### Camera

The camera eye position and lens are retained from Variant A:

```text
Position: (-0.620, -0.455, 1.450) m
Lens:     27 mm
```

Only the aim point changes:

```text
Previous aim: (2.800, -0.180, 1.390) m
Revision 3:  (4.800, -0.200, 0.380) m
```

The first Revision 3 render still hid the road behind the temporary dashboard. A second measured correction raised the temporary seated eye marker and camera to `Z = 1.450 m`, while retaining the same forward and lateral position. This exposes the road corridor without changing the RHD cockpit layout or moving the wheel, cluster, mirror, or hazard switch.

### Road and sign

The copied Revision 2 road/sign geometry is replaced only inside Revision 3 with:

- A continuous 8 m wide road surface.
- Raised shoulders on both sides.
- Separate road-edge strips.
- Three longitudinal lane-marking bands at `Y = -2.0, 0.0, +2.0`.
- Repeated markings from approximately `X = 2.2 m` through `X = 17.2 m` for visible perspective depth.
- A low median silhouette.
- A driver-side roadside board at approximately `(8.5, -4.08, 1.75) m`.
- Original temporary board text: **HIGHWAY ASSISTANCE**.

The sign is not a final Indian highway sign and is not copied from a real sign design.

## Render assessment

### Driver-eye render

`driver_eye_revision3_A_forward.png` demonstrates:

- A clearly visible three-dimensional road corridor through the windshield.
- Multiple lane-marking segments distributed in forward perspective.
- Distinguishable road edge and shoulder on the driver side.
- A readable roadside board with `HIGHWAY ASSISTANCE`.
- Steering wheel and instrument cluster retained in the right-hand-drive position.
- Separate red hazard switch still visible.
- Driver-side mirror still visible.

### Overall render

`cockpit_overall_revision3_forward.png` shows the cockpit blockout, road slab, shoulders, lane markings, median, and sign as separate spatial elements. It is a layout diagnostic, not a final environment render.

## Acceptance results

| Criterion | Result | Evidence |
|---|---|---|
| Road occupies meaningful forward view | **PASS for blockout** | Driver-eye render shows the road corridor in the upper forward view and foreground |
| Lane markings form natural corridor | **PASS for blockout** | Multiple marking segments recede toward the visible road horizon |
| Shoulder distinguishable from lanes | **PASS for blockout** | Raised tan shoulder and separate bright edge strips visible |
| Assistance sign identifiable | **PASS for blockout** | Board visibly reads `HIGHWAY ASSISTANCE` |
| Dashboard does not hide important view | **PASS provisionally** | Temporary dashboard remains prominent, but the road, sign and shoulder are visible above it |
| Steering wheel and cluster remain legible | **PASS** | Existing right-side wheel and cluster geometry preserved |
| Driver-side mirror remains legible | **PASS** | Mirror remains visible at the right edge of driver-eye render |
| Hazard switch remains separate and legible | **PASS** | `BTN_HazardSwitch` remains an independent red mesh |
| No new camera clipping/intersections | **PASS provisionally** | Raised eye marker and camera render without visible clipping or cockpit intersections |

## Limitations

- Road, lane markings, shoulders, median, and sign are temporary geometry.
- The temporary sign uses text geometry for composition testing only.
- The windshield remains a blockout opening, not final glass.
- No traffic, detailed materials, driving physics, mechanic, tyre repair, or RealityKit/USDZ validation was added.
- The render demonstrates the composition gate, not production visual quality.

## Review recommendation

Retain Variant A's eye position with the Revision 3 aim correction as the preferred composition candidate. Do not proceed to Stage 2 until the rendered road corridor, lane markings, shoulder, sign, steering wheel, cluster, mirror, and hazard switch are explicitly reviewed and accepted.
