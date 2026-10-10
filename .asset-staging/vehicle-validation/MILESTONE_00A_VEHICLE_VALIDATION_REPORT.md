# Milestone 00A Vehicle Validation Report

**Asset:** `spectral_gt_rs_master.blend`  
**Source:** `.asset-staging/spectral-gt-rs/spectral_gt_rs_master.blend`  
**Inspection date:** 2026-09-15  
**Inspector:** Blender 5.2.2 LTS, headless read-only inspection  
**Classification:** **FAIL — unsuitable for the benchmark realism and learning-vehicle target**

## Scope and method

The original Blender source was opened read-only. No source save, export, transform, material edit, mirroring, animation edit, or Reality Composer Pro import was performed. The inspection generated a structural report and four diagnostic renders:

- `vehicle_validation.json`
- `authored_cockpit_detail.png`
- `candidate_driver_eye.png`
- `negative_y_driver.png`
- `positive_y_passenger.png`

The renders are diagnostic evidence only. They are not a final visual-quality benchmark because the source file's studio lighting and authored camera setup produce very dark, high-contrast images in Blender 5.2.2's compatible Eevee renderer.

## Verified findings

### 1. Vehicle structure and scale

- The file uses metric units with `scale_length = 1.0` and metres as the length unit.
- The inspected scene contains 285 objects, 254 mesh objects, and 26 materials.
- The source contains separate collections for body panels, glass, aero/trim, wheels/brakes, interior, lights, mechanics, animation controls, cameras, and studio lighting.
- The global scene bounds include studio-stage and lighting content (`30 m x 30 m x 8.01 m`), so the bounds are not a reliable vehicle-only dimension measurement.
- The source documents a front axis of `+X` and a metre-scale authoring workflow.

### 2. Cockpit and driver-eye evidence

- Separate driver and passenger seat components exist, including seat bases, backs, bolsters, headrests, and shoulder belts.
- A separate `Steering_Wheel` mesh exists and is parented to `STEERING_INPUT_CTRL`.
- `STEERING_INPUT_CTRL` is located at approximately `[0.40, -0.49, 1.18]`.
- Driver-seat components are centred around `Y = -0.43`; passenger-seat components are centred around `Y = +0.43`.
- A dashboard core, digital gauge cluster, front windshield, rear-view mirror, and left/right exterior mirror shells are present.
- The source does **not** document which signed lateral axis represents the vehicle's left or right side. Therefore the negative-Y steering position is not sufficient proof of right-hand drive.
- The candidate driver-eye render does not establish a comfortable production driver's-eye composition. It is dominated by dark cockpit geometry and does not provide a clear, usable forward road view.
- The staged preview and diagnostic renders show a stylized sports-car cockpit rather than a conventional modern Indian-market sedan interior.

**RHD result:** **Unverified.** The source must not be accepted as right-hand drive without an explicit vehicle-axis convention and an inspection render showing steering wheel, gauge cluster, driver seating, windshield, and mirror sightlines together.

### 3. Hazard switch

- The validation inventory contains no mesh assigned to `HazardSwitch` and no mesh assigned to `Hazard`.
- No verified separate hazard-light control was found in the inspected key-object inventory.
- The existing dashboard geometry may contain an unlabelled surface or button, but that cannot be treated as a functional hazard control without visual and object-level verification.

**Hazard-control result:** **Missing/unverified.** A benchmark interaction would require a custom, visibly identifiable hazard switch and a runtime-ready control entity.

### 4. Mirrors and windshield

- `Front_Windshield` and `Rear_Windshield` meshes exist.
- `L_Mirror_Shell` and `R_Mirror_Shell` meshes exist at approximately `Y = -0.829` and `Y = +0.829`.
- The cockpit render includes windshield/glass and a rear-view mirror, but the diagnostic driver-eye render does not demonstrate usable left/right mirror sightlines.
- Mirror shells are separate objects, but mirror reflection quality and driver-seat alignment remain unverified in RealityKit.

**Mirror/windshield result:** **Geometry present; usability unverified.**

### 5. Exterior lamps

- Separate headlight housing, main, and LED meshes exist on both sides.
- Separate tail-light housing, bar, and accent meshes exist on both sides.
- These objects are suitable candidates for later emissive/light-state wiring.
- No runtime light animation or hazard-synchronized lamp behavior was validated in this inspection.

**Lamp result:** **Geometry separated; runtime behavior unverified.**

### 6. Wheels and tyres

- Four named tyre assemblies are present: front/rear and left/right.
- Tyre block meshes are separately modelled around the tyre assemblies.
- Wheel hub and spoke meshes are present.
- The source provides useful wheel separation for later animation or replacement work.
- No spare wheel, luggage compartment, jack, or lug-wrench storage system was verified.

**Wheel result:** **Usable geometry separation; tyre-repair training compatibility not established.**

### 7. Doors, hood, and trunk

- `DOOR_L_CTRL` and `DOOR_R_CTRL` empties exist, with separate door-skin and trim meshes parented to the corresponding controls.
- `HOOD_SERVICE_CTRL` exists.
- The source reports authored door and hood animation actions.
- Blender 5.2.2 exposes the actions through its current layered animation API; the legacy `Action.fcurves` field is unavailable, so the structural report records the action frame ranges but not legacy curve counts.
- The key-object inventory contains no verified trunk mesh or trunk control.
- The sports-car/open-body presentation and the profile preview do not demonstrate a conventional usable sedan luggage compartment.

**Door/hood result:** **Promising for visual animation; trunk/storage requirement fails.**

### 8. Materials and visual realism

- The scene contains 26 materials and separate glass, body, trim, interior, wheel, brake, and light collections.
- The source is substantially more detailed than a primitive placeholder and is suitable for technical prototyping.
- The visual language is a stylized, low-slung sports car with exposed/open forms, not a realistic Indian-market sedan used for roadside safety training.
- The diagnostic renders show very dark exposure and high-contrast studio lighting. This is a validation-render limitation, not proof that the source materials are unusable in a correctly lit runtime scene.
- Material and texture fidelity inside RealityKit/USDZ remains unverified because Reality Composer Pro was unavailable and no import was performed.

## Acceptance assessment

| Requirement | Result | Evidence |
|---|---|---|
| Realistic RHD Indian-market sedan cockpit | **Fail** | RHD is unverified; vehicle is a stylized sports car |
| Driver-eye forward visibility | **Fail for benchmark** | Diagnostic driver-eye render does not show a usable road-facing composition |
| Windshield and mirrors | Partial | Separate meshes exist; sightlines not validated |
| Dashboard and instrument cluster | Partial | Separate dashboard/gauge meshes exist |
| Functional hazard control | Fail | No verified `HazardSwitch` or `Hazard` mesh in key-object inventory |
| Exterior lamp separation | Pass for geometry | Separate bilateral headlight/tail-light meshes exist |
| Wheel separation | Pass for geometry | Four named tyre assemblies and wheel components exist |
| Door animation structure | Partial | Door controls and actions exist; runtime import not validated |
| Trunk/luggage storage | Fail | No verified trunk/storage system |
| Tyre-repair learning vehicle | Fail | No spare-wheel/tool storage and unsuitable vehicle form |
| RealityKit/Reality Composer Pro readiness | Unverified | No Reality Composer Pro available; no import performed |

## Classification

### FAIL — unsuitable for our realism target

The model is a useful CC0 technical reference and may be valuable for testing object naming, wheel separation, lamp separation, and basic animation extraction. It should **not** be used as the first visual benchmark vehicle. The decisive blockers are:

1. Right-hand-drive layout is not proven.
2. The model is a stylized sports car rather than a realistic Indian-market sedan.
3. No verified hazard-switch mesh exists.
4. No verified trunk or luggage-storage system exists.
5. The driver's-eye render does not provide a credible benchmark view.
6. The model's open/sports-car form conflicts with the intended roadside tyre-emergency learning scenario.

Mirroring the model is not an approved remedy. Mirroring would require revalidating dashboard asymmetry, steering geometry, gauge placement, driver/passenger components, mirror visibility, materials, normals, transforms, and all animations, and it would not solve the missing sedan/trunk/hazard requirements.

## Recommended next steps

1. Do not import this vehicle into the production Reality Composer Pro scene.
2. Retain it in staging as a reference/prototyping asset only.
3. Acquire or commission a coherent right-hand-drive Indian-market sedan with:
   - a complete enclosed cabin;
   - explicit RHD steering and instrument cluster;
   - usable windshield and side mirrors;
   - a separately identifiable hazard switch;
   - separately addressable exterior lamps and wheels;
   - doors and boot/trunk geometry;
   - documented scale and USD/USDZ or Blender source.
4. Require an individual asset-page and licence review before download or import.
5. Re-run the same validation checklist on any replacement before production integration.

## Repository-safety check

This validation added only files under `.asset-staging/vehicle-validation/`. No production Swift source, Xcode project, build setting, or Reality Composer Pro content was modified by the validation work. Existing unrelated AppleDouble working-tree changes were left untouched.
