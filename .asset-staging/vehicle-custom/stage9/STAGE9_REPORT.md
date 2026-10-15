# Stage 9B Report

## Scope

Stage 9B replaces the broad SwiftUI action-area drag with entity-level RealityKit
targeting, adds a lightweight passing-traffic corridor and mirror safety gate,
adds visionOS RealityView attachments, adds the offline SSC compliance sheet,
and packages a clean submission archive. `.asset-staging/` remains outside the
Swift package.

## Files and final sizes

### Created or modified Swift files

| Path | Status | Bytes |
|---|---:|---:|
| `BeyondSchool.swiftpm/Sources/BeyondSchoolApp.swift` | modified | 9,372 |
| `BeyondSchool.swiftpm/Sources/RealitySceneController.swift` | modified | 14,506 |
| `BeyondSchool.swiftpm/Sources/ScenarioStateMachine.swift` | modified | 14,903 |
| `BeyondSchool.swiftpm/Sources/TrafficCorridorController.swift` | created | 3,455 |
| `BeyondSchool.swiftpm/Sources/SSCComplianceSheet.swift` | created | 1,626 |
| `BeyondSchool.swiftpm/Sources/SpatialAudioEngine.swift` | Stage 9A retained | 9,299 |
| `BeyondSchool.swiftpm/Sources/MechanicalKinematics.swift` | retained | 3,374 |

### Submission measurements

- `BeyondSchool.swiftpm`: 3,808 KiB disk usage (`du -sk`), approximately 3,899,392 bytes of allocated package storage.
- `.asset-staging/vehicle-custom/stage9/BeyondSchool_SSC_Submission.zip`: 1,233,525 bytes.
- No `.build`, `._*`, or `.DS_Store` files are present in the packaged Swift package.
- The archive remains well below the 5 MB working target and 20–22 MB SSC cap.

## Per-entity targeting and traffic verification

- The controller's interactive list contains all 17 requested nodes:
  `BTN_HazardSwitch_Pivot`, `CONSOLE_GearSelector_Pivot`,
  `CTRL_ParkingBrake_Pivot`, `MIRROR_Driver`, `DOOR_DriverRight_Pivot`,
  `TRUNK_Lid_Pivot`, `WHEEL_RL_FlatTarget`, five lug pivots,
  `JACK_Point_RL`, `WHEEL_Spare_Pivot`, `TOOL_ScissorJack_Root`,
  `TOOL_LugWrench_Root`, and `TOOL_WarningTriangle_Root`.
- Binding derives collision box extents from each entity's visual bounds,
  installs `InputTargetComponent(allowedInputTypes: [.direct, .indirect])`,
  and installs `HoverEffectComponent` only on visionOS.
- visionOS `RealityView` uses `SpatialTapGesture().targetedToAnyEntity()` and
  `DragGesture().targetedToAnyEntity()`, resolving the hit entity through its
  hierarchy to one of the 17 stable names.
- Out-of-order lug taps return failure and coach:
  “Use the five-point star order to distribute clamp load and prevent
  brake-rotor warping.”
- `TrafficCorridorController` maintains two low-poly traffic entities on
  `Y = -3.6 m`, advancing from `-X` to `+X`. The danger interval is
  `X ∈ [-18, +4]`. The model blocks driver-door opening while occupied and
  allows it after the gap clears.
- Focused smoke test passed for the 17-node inventory, danger-zone occupancy,
  blocked/allowed door opening, and out-of-order lug coaching.

## Attachments, comfort, and compliance

- visionOS `RealityView` attachments provide a glass-background instruction
  callout above the active target and a live five-stud diagram:
  `00 → 02 → 04 → 01 → 03`. RealityView attachment entities carry the
  `ViewAttachmentComponent` supplied by the visionOS attachment system.
- Manual and Assisted procedure controls remain available through the existing
  state machine.
- “Smooth camera glide” and “English subtitles” controls are exposed in the
  shared trainer view; drag scaling uses the comfort preference.
- `SSCComplianceSheet.swift` provides offline provenance, AI-assistance
  disclosure, and the 1033 Indian Highway safety disclaimer.

## Build and test output

Both final builds completed with exit code 0 and zero compiler warnings:

```text
swift build --package-path BeyondSchool.swiftpm \
  --build-path /tmp/stage9b-mac-final
Build complete! (13.77 sec)
```

```text
swift build --package-path BeyondSchool.swiftpm \
  --build-path /tmp/stage9b-xros-final \
  --sdk /Applications/Xcode.app/Contents/Developer/Platforms/XROS.platform/Developer/SDKs/XROS.sdk \
  --triple arm64-apple-xros27.0
Build complete! (12.24 sec)
```

The focused Stage 9B smoke test passed:

```text
Stage 9B targeting/traffic smoke passed
```

## Honest self-critique and readiness

Stage 9B is packaged and build-verified, but final human validation is still
required on the visionOS Simulator and Apple Vision Pro. The low-poly traffic
vehicles are intentionally procedural and visually minimal; a later visual
polish pass can add richer silhouettes without changing the safety gate. The
current SwiftUI trainer remains a compact benchmark surface rather than the
final three-minute SSC presentation flow. Final submission work should validate
hand/gaze ergonomics, accessibility with VoiceOver, subtitle timing, attachment
placement at multiple scales, audio loudness, interruption recovery, and the
official SSC signing/upload workflow.
