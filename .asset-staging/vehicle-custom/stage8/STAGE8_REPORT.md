# Stage 8 Report

## Scope

Stage 8 adds continuous mechanical kinematics, chassis lift/sag behavior, night
recall lighting hooks, direct drag manipulation routing, and procedural PCM cue
generation to the shared `BeyondSchool.swiftpm` RealityKit core. The Stage 6
USDZ remains the only 3D runtime asset inside the Swift package; source Blender
files, renders, and raw staging textures remain outside the package.

## Stage 6/7 baseline and size check

- Stage 6 evaluated scene: 426 objects, 49,674 evaluated vertices, 98,024 evaluated triangles.
- Stage 6 USDZ packaged in the runtime: 3,256,643 bytes.
- Stage 7 package folder baseline: approximately 3.7 MB; Stage 8 final disk usage is exactly 3,776 KiB (`du -sk`), approximately 3.866 MB decimal / 3.688 MiB.
- Stage 8 compressed archive: exactly 1,228,014 bytes, approximately 1.228 MB decimal / 1.171 MiB.
- No `.build` directory or AppleDouble `._*` files remain in the package.
- The package and archive remain below the requested 5 MB target and the SSC 20–22 MB cap.

## Files created or modified

| Path | Stage 8 status | Size |
|---|---:|---:|
| `BeyondSchool.swiftpm/Sources/MechanicalKinematics.swift` | created | 3,374 bytes |
| `BeyondSchool.swiftpm/Sources/SpatialAudioEngine.swift` | created | 2,240 bytes |
| `BeyondSchool.swiftpm/Sources/RealitySceneController.swift` | modified | 12,006 bytes |
| `BeyondSchool.swiftpm/Sources/BeyondSchoolApp.swift` | modified | 6,285 bytes |
| `BeyondSchool.swiftpm/Sources/ScenarioStateMachine.swift` | retained and smoke-tested | 14,256 bytes |
| `BeyondSchool.swiftpm/Package.swift` | retained | 466 bytes |
| `BeyondSchool.swiftpm/Sources/Resources/beyond_school_vehicle_scene.usdz` | retained runtime asset | 3,256,643 bytes |
| `BeyondSchool.swiftpm/Sources/Resources/blinker01.wav` | retained runtime asset | 135,494 bytes |
| `BeyondSchool.swiftpm/Sources/Resources/door_opening.wav` | retained runtime asset | 174,544 bytes |
| `BeyondSchool.swiftpm/Sources/Resources/door_closing.wav` | retained runtime asset | 126,088 bytes |

## Kinematic and audio verification

- Flat-tyre chassis sag reaches the configured 1.8° roll and pitch targets.
- Jack progress is clamped and smooth-stepped to a 65 mm maximum chassis lift;
  frame stepping converges through the spring interpolation path.
- The wrench/lug model supports the required `00 → 02 → 04 → 01 → 03` order,
  full 360° lug rotation, and 35 mm outward travel for a removed lug.
- Flat-wheel pull and spare-wheel swap progression values reach their configured
  220 mm travel parameters.
- `RealitySceneController` applies continuous updates through
  `SceneEvents.Update`, couples the wrench to the selected lug, and routes
  drag gestures to the active mechanical target.
- Recall mode installs headlamp spotlights, six hazard point-light components,
  the camera flashlight hook, and a passing-traffic whoosh attachment at
  `MIRROR_Driver`.
- Procedural PCM buffers were generated successfully for the 68 Hz flat-tyre
  thump, 420 Hz wrench creak, 1,100 Hz jack click, and 180 Hz traffic whoosh.
- The current zero-file-size audio implementation records generated buffers and
  entity attachments. It does not connect a separate `AVAudioEngine` output
  graph because the visionOS 27 `connect` API is deprecated while the
  replacement API is unavailable under the package's macOS 15 compatibility
  target. Bundled RealityKit audio remains active for the blinker and door cues.

## Build and test output

Both clean package builds completed with exit code 0 and no compiler warnings:

```text
swift build --package-path BeyondSchool.swiftpm \
  --build-path /tmp/beyond-stage8-mac
Build complete! (18.00 sec on final validation)
```

```text
swift build --package-path BeyondSchool.swiftpm \
  --build-path /tmp/beyond-stage8-xros \
  --sdk /Applications/Xcode.app/Contents/Developer/Platforms/XROS.platform/Developer/SDKs/XROS.sdk \
  --triple arm64-apple-xros27.0
Build complete! (14.43 sec on final validation)
```

Additional smoke checks passed:

- Mechanical kinematics and procedural audio invariant smoke test: passed.
- Complete guided state-machine flow, including all five lug actions and final
  transition to `recallChallenge`: passed.

## Honest self-critique and Stage 9 readiness

Stage 8 is structurally ready for Stage 9 integration, but it is not a
substitute for device validation. The remaining work is to connect the
procedural buffers to a supported spatial audio output graph for each target,
replace the current gesture-area routing with production hand/gaze targeting,
validate lighting and collision behavior in the visionOS Simulator and on Apple
Vision Pro hardware, and perform the final accessibility review. Stage 9
should also verify the complete three-minute guided/replay flow, interruption
recovery, narration/subtitles, and final SSC packaging/signing constraints.
