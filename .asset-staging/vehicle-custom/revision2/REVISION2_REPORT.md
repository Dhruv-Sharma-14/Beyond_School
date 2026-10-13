# Milestone 00C.1 Revision 2 — Forward Road Visibility

**Status:** Ready for review  
**Source preserved:** `../revision/beyond_school_cockpit_blockout_revision.blend`  
**Revision file:** `beyond_school_cockpit_blockout_revision2.blend`  
**Preferred camera:** `CAM_REV_A_balanced`  
**Scope:** Temporary forward-road composition test only

## Deliverables

- `beyond_school_cockpit_blockout_revision2.blend`
- `driver_eye_revision2_A_road.png`
- `cockpit_overall_revision2_road.png`
- `create_forward_road.py`

The original blockout and previous composition revision remain unchanged.

## Geometry added

The copied Revision 1 scene received temporary geometry only:

- `REV2_RoadSurface`: three-dimensional road surface extending forward from the cockpit.
- `REV2_LeftShoulder` and `REV2_RightShoulder`: raised shoulder strips.
- `REV2_LeftRoadEdge` and `REV2_RightRoadEdge`: visible road-edge lines.
- `REV2_LaneMark_*`: repeated lane markings across the forward road.
- `REV2_MedianBase`: low median/depth silhouette.
- `REV2_AssistanceSign_*`: roadside assistance sign board, face, cross silhouette, and post.

The former placeholder road and horizon objects were removed only from the copied Revision 2 scene so the new geometry is unambiguous. No production environment assets were used.

## Camera

The preferred camera is the existing Variant A camera:

```text
CAM_REV_A_balanced
Position: (-0.620, -0.455, 1.310) m
Aim:      ( 2.800, -0.180, 1.390) m
Lens:     27 mm
Resolution: 1280 x 720
```

No camera change was made to the preferred Variant A transform. The road was moved into the forward scene volume and given explicit surface, shoulder, edge, marking, median, and sign geometry.

The supplementary overall camera is:

```text
CAM_REV2_Overall
Position: (4.800, -6.800, 3.000) m
Aim:      (4.400,  0.000, 0.750) m
Lens:     42 mm
```

## Acceptance assessment

| Criterion | Result | Evidence |
|---|---|---|
| Road visibly three-dimensional | **PASS for temporary blockout** | Raised road surface, shoulders, edges, lane markings, and median are separate geometry |
| Lane markings visible | **PASS** | Repeated yellow lane markings are placed in the forward camera volume |
| Road edge and shoulder visible | **PASS for blockout** | Raised shoulder strips and edge lines flank the road |
| Assistance sign in forward view | **PASS for blockout** | Red/white roadside sign silhouette is placed on the driver-side shoulder |
| Dashboard obstruction controlled | **PASS provisionally** | Revision 1 dashboard and Variant A composition retained; road/horizon is above dashboard |
| Steering wheel and cluster retained | **PASS** | Existing `STEERING_ROOT`, `STEERING_Wheel`, and `DASH_InstrumentCluster` are unchanged in the copied revision |
| Driver-side mirror retained | **PASS** | Existing `MIRROR_Driver` remains in the copied scene |
| Hazard switch retained | **PASS** | `BTN_HazardSwitch` remains independent and visible in the cockpit render |
| No camera clipping/intersection | **PASS provisionally** | Camera transform is unchanged from accepted Variant A; overall view also renders without clipping |

## Limitations

- The road, shoulder, lane markings, median, and sign are temporary blockout geometry, not production artwork.
- The sign is a silhouette and contains no final Indian highway typography or branding.
- No traffic, driving physics, mechanic, tyre-repair interactions, detailed materials, or production environment assets were added.
- The render demonstrates composition and depth cues, not final visual realism.
- RealityKit/USDZ import and Apple Vision Pro validation remain pending.

## Review recommendation

Retain `CAM_REV_A_balanced` as the preferred camera. Approve progression only after reviewing both renders and confirming that the roadway, lane markings, shoulder, sign, steering wheel, cluster, mirror, and hazard switch are all legible together. Do not begin Stage 2 until this composition gate is explicitly accepted.
