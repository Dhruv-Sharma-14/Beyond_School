# Beyond School — Stage 3 Interior PBR Materials, Cluster Graphics & Cabin Lighting

**Status:** Ready for review  
**Source:** `../stage2_1/beyond_school_stage2_1_dashboard.blend`  
**Output:** `beyond_school_stage3_interior_pbr.blend`

## Deliverables and sizes

| File | Size |
|---|---:|
| `create_stage3_materials.py` | 17.7 KB |
| `beyond_school_stage3_interior_pbr.blend` | 270.5 KB |
| `driver_eye_stage3.png` | 1229.4 KB |
| `dashboard_controls_stage3_close.png` | 1179.9 KB |
| `cockpit_overall_stage3.png` | 1085.6 KB |

## Stage 2.1 baseline metrics

- Stage 2.1 unique mesh vertices: **7,804**.
- Stage 2.1 unique mesh triangles: **14,964**.
- Main dashboard bounds from the source: `DASH_UpperShell` `(0.4285, 1.6000, 0.2055) m`; `DASH_LowerFascia` `(0.3837, 1.5800, 0.2473) m`; `DASH_InstrumentCluster` `(0.0140, 0.3000, 0.1250) m`; `CONSOLE_CentreStack` `(0.2800, 0.5200, 0.5700) m`.
- The Stage 2.1 report did not state numeric sightline clearance values. Recomputed for this derivative: camera-to-upper-shell vertical clearance `0.284 m`; cluster front position `X=0.424 m`; preserved eye position `(-0.620, -0.455, 1.290) m`.

## Stage 3 implementation

- Applied USDZ-safe Principled BSDF materials for soft-touch polyurethane, graphite polymer, satin gunmetal, leather, rubber, pedals, road, markings, and sign.
- Generated compact original 1024×512 PNG graphics for the cluster and infotainment display. The cluster graphic contains km/h/RPM dial arcs and an amber/red tyre warning state; the infotainment graphic contains an unbranded four-lane navigation/status view with a rear-left tyre alert.
- Added subtle cabin bounce and cluster fill lights. Loaded the staged Qwantani noon HDRI when present: `/Volumes/DHRUV/Beyond_School/.asset-staging/polyhaven/qwantani_noon_puresky/2k/qwantani_noon_puresky_2k.hdr`.
- Preserved the deterministic interaction hierarchy, metric scale, camera, steering pivots, road geometry, and previous-stage files.

## Validation

- Blender 5.2.2 headless generation: **PASS**.
- Reopen and active camera `REV4_Camera_MID`: **PASS**.
- Metric units, scale 1.0, 1280×720 output: **PASS**.
- Required interaction names and pivots: **PASS**; no duplicate required names.
- Stage 3 mesh totals: **8,332 vertices / 16,012 triangles**.
- Texture budget: two 1024×512 PNGs, compact and below the requested 1024² maximum; no 4K textures.
- Materials use Principled BSDF inputs only; procedural noise/bump graphs were not introduced.

## Visual inspection and self-critique

- Driver's-eye render: cluster warning graphics, hazard switch, steering assembly, mirror, road corridor, shoulder, and assistance sign remain visible. The warning is intentionally high contrast but remains a diagnostic graphic rather than final typography.
- Close-up render: satin trim, darker recesses, crimson hazard cap, stepped climate rings, and display emissions separate the controls more clearly than Stage 2.1.
- Overall render: cabin and road remain readable under the HDRI/fill setup without changing the preferred camera.
- Remaining limitations: the temporary cockpit/road geometry is still a blockout, the cluster texture is a compact generated diagnostic, no USDZ export or Vision Pro profiling has been performed, and final PBR microdetail remains deferred.

## Recommendation

Stage 3 is ready for review before USDZ export and the shared RealityKit core integration milestone. Do not modify Stage 2.1 or earlier revisions.
