# Beyond School — Stage 4.1 Exterior Aperture and Silhouette Refinement

**Status:** Generated, rendered, reopened, and validated  
**Source:** `../stage4/beyond_school_stage4_exterior_body.blend`  
**Output:** `beyond_school_stage4_1_exterior_refined.blend`

## Files and sizes

| File | Size |
|---|---:|
| `create_stage4_1_exterior.py` | 30.9 KB |
| `beyond_school_stage4_1_exterior_refined.blend` | 329.5 KB |
| `driver_eye_stage4_1.png` | 1417.6 KB |
| `dashboard_controls_stage4_1_close.png` | 1295.7 KB |
| `exterior_front_right_stage4_1.png` | 1161.7 KB |
| `exterior_rear_left_stage4_1.png` | 1214.5 KB |
| `exterior_open_door_trunk_stage4_1.png` | 1173.3 KB |

## Zero-hiding and aperture verification

- All five renders were produced with all exterior objects visible; no exterior mesh was hidden for interior views.
- The script asserts `hide_render == False` and `hide_viewport == False` for the shell, roof, hood, driver door, windshield, driver mirror, and all marked exterior objects.
- Windshield aperture center: `(0.720, 0.000, 1.200) m`; camera-to-center distance: `1.418 m`.
- Driver doorway bounds: A-pillar `X=+0.730`, B-pillar `X=-0.350`, sill top `Z=0.510`, roof rail bottom approximately `Z=1.350`.
- Trunk cavity: `0.720 × 1.050 m`, floor at `Z=0.650 m`, split deck panels leave the well open.

## Stage 4.1 implementation

- Replaced the transverse Stage 4 shell with a perimeter greenhouse: side sills, beltline, shoulder, A/B/C pillars, roof rails and header.
- Added a sloped hood/cowl, recessed front grille and lower air dam, rear license recess, and separate lamp-support surfaces.
- Rebuilt driver/passenger/rear door portals as lower skins plus four-sided window frames and alpha-0.08 clear glazing.
- Added dark inner wheel-arch liners and slim flares around all four wheel centers.
- Split the trunk deck around the hollow `TRUNK_WellCavity`; open diagnostic pose uses driver door `-55°` and trunk `+62°`, then resets both pivots to `0°` before saving.

## Validation and visual review

- Blender 5.2.2 headless generation/reopen: **PASS**.
- Metric scale 1.0, active saved camera `REV4_Camera_MID`, required names and pivots: **PASS**.
- Mesh totals: **13,020 vertices / 24,980 triangles**; triangle budget `<30,000`: **PASS**.
- Open pose test and closed-state save: **PASS**.
- All five PNGs are 1280×720.
- Driver-eye and dashboard-close views retain the road, sign, cluster, steering wheel and controls while the exterior remains loaded.
- Closed exterior views show the refined greenhouse, side glazing, beltline, lamps and wheel arches.
- Open diagnostic visibly demonstrates the driver doorway and trunk well; the exterior remains a benchmark shell rather than final production surfacing.

## Recommendation

Stage 4.1 is ready as the source for Stage 5 removable rear-left flat tyre, spare wheel, scissor jack and lug-wrench assemblies, subject to visual approval.
