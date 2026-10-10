# Beyond School — Asset Staging Report

Checked: 2026-10-10  
Staging root: `.asset-staging/`  
Production Swift source and Xcode build settings: unchanged.

## 1. What was staged

The staging directory contains:

- The CC0 vehicle repository, including editable Blender source, game-ready GLB, source script, README/license, handoff notes, and six preview renders.
- 2K Poly Haven asphalt material maps.
- A 2K Poly Haven clear midday HDR.
- A 2K Poly Haven concrete road barrier in USD plus material maps.
- A 2K Poly Haven worn tyre in USD plus material maps, explicitly retained as a reference rather than a spare-wheel asset.
- Five CC0 prototype WAV files from the two selected OpenGameArt pages.
- This manifest and report.

No production scene, Swift source, Xcode project file, Reality Composer Pro project, or app asset catalog was changed.

## 2. Vehicle inspection

### Verified from the source repository and source script

- The vehicle is a procedural sports-car asset, not an Indian-market sedan.
- The source states Blender 5.1.2 authoring and meter scale.
- The vehicle front axis is `+X`.
- The game-ready GLB is binary glTF 2.0 and approximately 4.7 MB.
- The GLB export contains 263 objects, including 59 mechanical-detail objects, according to `REALTIME.md`.
- The source declares separate body, glass, aero/trim, wheels/brakes, cockpit, lights, and mechanics collections.
- The source script explicitly creates:
  - front windshield and rear windshield,
  - left/right exterior mirror shells and stalks,
  - dashboard, vents, center display, seats, rear-view mirror,
  - steering wheel, hub, spokes, and digital gauge cluster,
  - left/right wheel assemblies with tyres, brake discs, calipers, rims, hubs,
  - headlight and tail-light housings/bars,
  - separate left/right door controllers and door skins,
  - hood service controller,
  - steering animation controller.
- The source documents these clips: `Doors_PingPong`, `Doors_PingPong.001`, `Hood_Service_PingPong`, and `Steering_Input_PingPong`.

### Not verified because Blender is unavailable

- Whether the driver position is right-hand drive. The script places `Driver` and `Steering_Wheel` at negative Y, but the repository does not establish which lateral sign corresponds to the vehicle's right-hand side. It must not be treated as RHD evidence.
- Driver's-eye visibility and comfort from the actual camera/eye position.
- Correct alignment of the steering wheel with the instrument cluster from the user's seated viewpoint.
- Whether the hazard-light control exists as a distinct physical control. The source identifiers include dashboard/display/vent elements but no explicit hazard-switch object was found in the inspected source region.
- Whether mirrors provide a usable view rather than merely existing as geometry.
- Whether exterior lights are separated into useful runtime entities/material slots for hazard animation.
- Whether door animations preserve useful transforms and collision behavior after import.
- Whether wheel assemblies can be reused for a learning vehicle or independently addressed in RealityKit.
- Whether the trunk/luggage area can hold a spare wheel, jack, or tools. The current sports-car source is not approved for tyre-replacement training.

### Current vehicle decision

**Staging candidate only — not approved as the final learning vehicle.**

The asset has unusually strong structural evidence for a zero-cost candidate: real cockpit geometry, glazing, mirrors, lights, wheel separation, source scene, and animations. However, it is a sports car and the critical product requirements remain unresolved:

1. RHD layout.
2. A distinct, interactable hazard switch.
3. Sedan-like ergonomics and storage suitable for later roadside learning.
4. Trunk/spare-wheel feasibility.
5. RealityKit/Reality Composer Pro material and animation fidelity after import.

Do not mirror the model until Blender inspection confirms that steering, gauges, asymmetrical dashboard elements, mirrors, pedals, labels, animations, and material orientation remain coherent. Mirroring is not a valid substitute for verified RHD geometry.

## 3. Environment inspection

### Asphalt

`clean_asphalt` was staged at 2K. It is a material, not a road environment. The highway mesh, lane widths, shoulder, median, road markings, and Gujarat-inspired dressing must still be authored.

### Daylight

`qwantani_noon_puresky_2k.hdr` is a valid Radiance HDR and the selected source page describes a clear midday, high-contrast pure sky. It is suitable as a lighting candidate, not a geographic representation of Gujarat.

### Barrier

`concrete_road_barrier_2k.usdc` passed `usdcat` structural parsing. The individual page describes a weathered barrier with chipped black-and-white checker paint, dirt streaks, eroded edges, and rusted lifting loops. This may conflict with the approved clean, good-quality fictional highway. The asset is therefore **staged but not approved for final use**; it should be recolored/retextured only if the CC0 source is retained and the result matches the visual direction, or replaced with an in-house clean median/safety barrier.

### Tyre

`old_tyre_2k.usdc` passed the same USD structural check. It is explicitly a worn tyre reference and is not a suitable new spare-wheel asset. No spare wheel, jack, or lug wrench was created.

## 4. Audio inspection

The two selected OpenGameArt pages exposed CC0 license indicators. The downloaded filenames were preserved:

- `blinker01.wav`
- `blinker02.wav`
- `blinker03.wav`
- `door_closing.wav`
- `door_opening.wav`

The WAV files were verified by `file` as 44.1 kHz IEEE-float audio. They are prototype interaction sounds only. They do not provide cabin/road ambience or a spatial traffic pass-by, so those remain missing.

## 5. Conversion/import validation

| Check | Result |
|---|---|
| Vehicle source clone | Passed; repository cloned at staging commit `34499c501908818a2b08e589a7aecf963343cee7` |
| Vehicle GLB file type | Passed; glTF binary model, version 2 |
| Vehicle GLB size | Passed; 4,688,844 bytes |
| Vehicle previews | Present; six 1280×720 PNG renders |
| Barrier USD syntax | Passed with `/usr/bin/usdcat` |
| Tyre USD syntax | Passed with `/usr/bin/usdcat` |
| HDR file type | Passed; Radiance HDR |
| Prototype WAV file types | Passed; 44.1 kHz WAV files |
| Blender visual inspection | Blocked; Blender is not installed |
| Reality Composer Pro import | Blocked; Reality Composer Pro is not available in this environment |
| Apple Vision Pro validation | Blocked; no device available |
| Conversion | None performed |

## 6. Missing assets and blockers

### Required before the visual benchmark

- A verified right-hand-drive learning vehicle, or approval to adapt the sports-car candidate only after Blender inspection.
- A distinct hazard switch mesh/entity and dashboard feedback material/animation.
- A clean, highway-compatible median/safety barrier or an approved retexture of the staged barrier.
- Authored four-lane divided highway geometry with left-hand traffic paths.
- Gujarat-inspired roadside dressing and custom Indian-style signs.
- Three to six traffic vehicles; Kenney remains unverified and must not be placed near the foreground until visual quality is tested.
- Cabin/road ambience.
- Spatial traffic pass-by audio.

### Technical blockers

- No Blender executable in the development environment.
- No Reality Composer Pro application available.
- No Apple Vision Pro hardware available.
- No verified spare-wheel/trunk suitability for the sports-car candidate.

## 7. Recommended next decision

Treat the staged vehicle as a **technical pipeline candidate**, not the final learning car. The lowest-risk path is:

1. Inspect the `.blend` in Blender on a machine with Blender 5.1.x.
2. Confirm lateral orientation, driver eye marker, steering/gauge alignment, hazard-control availability, mirror visibility, light separation, door animation, wheel separation, and luggage storage.
3. If any of those fail, reject the candidate rather than mirroring it silently.
4. Continue with the staged 2K asphalt/HDR foundation and custom road/sign geometry.
5. Keep the barrier staged for comparison only; prefer a clean custom barrier if the checker/weathered finish conflicts with the visual direction.
6. Do not acquire or integrate traffic, Mixamo, spare-wheel, or mechanic assets in this milestone.

## 8. License caveat

The manifest records source-page evidence rather than legal advice. CC0 permits copying, modification, distribution, and commercial use, but it does not independently verify the underlying copyright status of every work. Preserve each source URL, author, download date, filename, and hash with any future conversion or import.

