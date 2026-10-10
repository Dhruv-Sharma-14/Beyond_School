# Beyond School — Custom Sedan Cockpit Reference and Measurement Sheet

## Design direction

This is an original, unbranded compact-to-mid-size Indian-market sedan cockpit. It is designed for a first-person roadside-emergency learning experience, not as a reproduction of a particular production vehicle.

- Four-door notchback sedan proportions.
- Right-hand-drive seating and controls.
- +X forward, -X rearward, -Y driver side, +Y passenger side, +Z up.
- Dark soft-touch dashboard, fabric/synthetic-leather seats, restrained satin trim.
- Original lamp, wheel, switch, display, grille, and body-surface design.
- No manufacturer logos, badges, protected graphics, or copied trim signatures.

## Proposed design dimensions

These are blockout targets, not certified vehicle or homologation measurements.

| Measurement | Target |
|---|---:|
| Overall length | 4.430 m |
| Body width excluding mirrors | 1.765 m |
| Overall height | 1.485 m |
| Wheelbase | 2.600 m |
| Front track | 1.530 m |
| Rear track | 1.535 m |
| Ground clearance | 0.165 m |
| Driver seat H-point height | approximately 0.635 m |
| Dashboard upper surface | approximately 1.18 m |
| Steering-wheel centre | approximately 1.18 m |
| Initial driver-eye marker | `(-0.350, -0.455, 1.285)` m |

The driver-eye marker was moved rearward from the initial blueprint estimate of `(+0.250, -0.455, 1.285)` m during composition testing. The rearward position produced a more believable seated relationship to the steering wheel instead of a camera nearly touching it. This is an intentional blockout adjustment requiring review.

## Coordinate convention

```text
                 +X forward
                     ^
                     |
       +Y passenger  |  -Y driver
              <------+------>
                     |
                 -X rearward
                     +Z up
```

- Origin: wheelbase centre at ground level.
- Driver seat, steering wheel, driver mirror, and driver interaction markers use negative Y.
- Passenger seat and passenger mirror use positive Y.
- Blender scene units are metres.

## Reference material

The following sources are reference-only. Their photographs, diagrams, logos, and distinctive design details are not included in the staged Blender asset.

| Source | Features studied |
|---|---|
| [Honda Amaze specification leaflet](https://www.hondacarindia.com/web-data/brochures/pdfs/04022025_Amaze%20Spec_Leaflet%20Rev%20copy.pdf) | Compact Indian sedan dimensions, cabin packaging, RHD driver position |
| [Honda India brochures](https://www.hondacarindia.com/brochure) | RHD dashboard proportions, seating and windshield relationship |
| [Hyundai Verna brochure](https://www.hyundai.com/content/dam/hyundai/in/en/data/brochure/verna.pdf) | Modern dashboard layering, display placement, trim contrast |
| [ARAI AIS downloads](https://www.araiindia.com/downloads/ais-downloads) | Regulatory context for Indian automotive controls and mirrors |
| [Blender glTF exporter documentation](https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html) | Stable hierarchy, transform, naming, and material-export planning |
| [Apple RealityKit rendering guidance](https://developer.apple.com/documentation/visionos/reducing-the-rendering-cost-of-realitykit-content-on-visionos) | Provisional real-time mesh/material and profiling considerations |

## Original layout sketch

### Top view

```text
                         +X forward
              windshield / road opening
        +--------------------------------------+
        |  MIRROR_Driver       MIRROR_Passenger|
        |                                      |
        |  [driver seat]  steering  [passenger]|
        |       -Y          O       +Y         |
        |                  [dash]              |
        |              [hazard switch]         |
        |             transmission tunnel      |
        +--------------------------------------+
                         -X rearward
```

### Driver-eye view intent

```text
        side mirror        windshield / road horizon
             [ ]       ___________________________
                    __/                           \__
                   /      instrument cluster       \
                  |       (behind steering wheel)   |
                  |      steering wheel      [hazard]|
                  |________dashboard / console______|
```

The sketch is an original planning diagram and is not derived from a manufacturer's drawing.

## Assumptions requiring validation

1. The proposed dimensions provide a credible compact-to-mid-size sedan package.
2. The initial driver-eye marker is comfortable and does not intersect the seat, wheel, or dashboard.
3. A 24 mm Blender camera approximates a useful first-person diagnostic field of view; final visionOS composition may differ.
4. The temporary open windshield is sufficient for Stage 1 composition; final laminated glass and optical treatment are deferred.
5. The temporary road plane and horizon backdrop are adequate for cockpit composition only.
6. Final ergonomic validation requires the exported asset in RealityKit and, when available, Apple Vision Pro hardware.
7. Driver-side mirror placement and hazard-switch reach must be reviewed by human testers before detailed modelling.
