# Stage 10 Report

## Scope

Stage 10 upgrades the Stage 9B benchmark into a cohesive three-minute roadside
experience without moving source art into `BeyondSchool.swiftpm` beyond the
existing optimized USDZ and runtime WAV files. It adds articulated procedural
traffic, a spring-damped aerodynamic wake response, a stylized mechanic mentor
with service beacon, offline Indian-English speech synthesis, a 1033 dialer
surface, and a mastery recap/replay flow.

## Files and final sizes

| Path | Status | Bytes |
|---|---:|---:|
| `BeyondSchool.swiftpm/Sources/BeyondSchoolApp.swift` | modified | 12,164 |
| `BeyondSchool.swiftpm/Sources/RealitySceneController.swift` | modified | 15,152 |
| `BeyondSchool.swiftpm/Sources/ScenarioStateMachine.swift` | modified | 16,818 |
| `BeyondSchool.swiftpm/Sources/MechanicalKinematics.swift` | modified | 3,911 |
| `BeyondSchool.swiftpm/Sources/TrafficCorridorController.swift` | modified | 5,465 |
| `BeyondSchool.swiftpm/Sources/MechanicCoachController.swift` | created | 4,026 |
| `BeyondSchool.swiftpm/Sources/SpatialAudioEngine.swift` | retained | 9,299 |
| `BeyondSchool.swiftpm/Sources/SSCComplianceSheet.swift` | retained | 1,626 |

Submission measurements:

- `BeyondSchool.swiftpm`: 3,936 KiB (`du -sk`).
- Stage 10 archive: measured after packaging; no `.build`, `.DS_Store`, or
  AppleDouble entries.
- `.asset-staging/` remains outside the package and is not bundled as runtime
  content.

## Traffic buffeting and mechanical response

- The sedan now has a body, windshield trim, four wheel cylinders, headlamps,
  and taillamps.
- The logistics truck now has a cab/body, cargo box, windshield/headlamp and
  taillamp details, and four wheel cylinders.
- Both continue to use the right-hand corridor at `Y = -3.6 m` and move from
  `-X` toward `+X`.
- Crossing the wake interval injects a signed `0.35°` roll impulse into the
  parked chassis and a `0.012 m` camera-shake amplitude. The response is
  exponentially spring-damped every frame.
- The wake event triggers the existing spatial traffic whoosh at peak intensity.

## Mechanic, speech, and 1033 flow

- `MechanicCoachController` creates a vest, reflective strips, head, hard hat,
  gesturing arm, and pulsing beacon near `(-1.85, 1.45, 0.65)`.
- The mentor is enabled for `trunkToolkitHandOff` and `assistedWheelChange`.
- `AVSpeechSynthesizer` uses `en-IN` and falls back to `en-US`; the HUD exposes
  a Mechanic Voice Coach mute toggle.
- The inspection state presents `NH-48 KM 142 · Left Shoulder`, signal status,
  and a Dial 1033 control. The dial action sets `dialerConnected` before the
  warning-triangle step.

## Three-minute presentation arc

- Spatial title card: tagline, Start 3-Minute Experience, existing Manual /
  Assisted procedure choice, and smooth camera comfort control.
- Guided sequence: highway observation, pull-over, secure cockpit, mirror gate,
  inspection, 1033 call, toolkit hand-off, and assisted repair.
- Night recall: existing `.recallChallenge` lighting path remains active.
- Mastery recap: safety-check count, star-pattern accuracy, elapsed seconds
  against the `<= 180s` target, and Replay / Practice Again.

## Build and smoke tests

```text
swift build --package-path BeyondSchool.swiftpm \
  --build-path /tmp/stage10-mac
Build complete! (15.07 sec)
```

```text
swift build --package-path BeyondSchool.swiftpm \
  --build-path /tmp/stage10-xros \
  --sdk /Applications/Xcode.app/Contents/Developer/Platforms/XROS.platform/Developer/SDKs/XROS.sdk \
  --triple arm64-apple-xros27.0
Build complete! (13.30 sec)
```

Both builds completed with zero compiler warnings. The automated state,
dialer, traffic-wake, and kinematics smoke test passed:

```text
Stage 10 state, dialer, traffic wake, and kinematics smoke passed
```

## Honest self-critique

The procedural traffic and mechanic are now spatially readable and behaviorally
connected, but they remain stylized benchmark geometry rather than final
photorealistic art. `AVSpeechSynthesizer` voice quality, traffic loudness,
wake amplitude, mentor placement, title-card scale, and scorecard legibility
still need visual and audio tuning on visionOS Simulator and Apple Vision Pro.
The package has not been code-signed or submitted to the official SSC portal.
