# Beyond School — Asset Staging Manifest

Checked: 2026-10-10  
Scope: Milestone 00 visual benchmark staging only.  
Production source/build files were not modified.

## Staged and license-verified assets

| ID | Local path | Original filename/format | Source and author | License evidence | Attribution | Notes |
|---|---|---|---|---|---|---|
| VEH-001 | `spectral-gt-rs/spectral_gt_rs_master.blend` | `spectral_gt_rs_master.blend`, Blender source | [JaronKBragg7337/spectral-gt-rs](https://github.com/JaronKBragg7337/spectral-gt-rs), Jaron K. Bragg | Repository [README/license](https://github.com/JaronKBragg7337/spectral-gt-rs/blob/main/LICENSE) states the original model, source, renders, and showcase are CC0 1.0 | None required; credit appreciated | Authored in meters. Blender 5.1.2 source stated by repository. Visual/RHD checks require Blender. |
| VEH-002 | `spectral-gt-rs/spectral_gt_rs_game_ready.glb` | `spectral_gt_rs_game_ready.glb`, binary glTF 2.0 | Same source as VEH-001 | Same CC0 evidence | None required | 4,688,844 bytes; self-contained GLB; four clips documented: `Doors_PingPong`, `Doors_PingPong.001`, `Hood_Service_PingPong`, `Steering_Input_PingPong`. |
| VEH-003 | `spectral-gt-rs/spectral_gt_cockpit.png` and other `spectral_gt_*.png` files | PNG preview renders, 1280×720 | Same source as VEH-001 | Same CC0 evidence | None required | Preview evidence only; not runtime assets. |
| ENV-001 | `polyhaven/clean_asphalt/2k/clean_asphalt_diff_2k.jpg` | 2048×2048 JPEG diffuse | [Clean Asphalt](https://polyhaven.com/a/clean_asphalt), Poly Haven | [Poly Haven license](https://polyhaven.com/license) and CC0 asset metadata | None required | Material map only; no road mesh or lane-marking layout. |
| ENV-002 | `polyhaven/clean_asphalt/2k/clean_asphalt_nor_gl_2k.jpg` | 2048×2048 JPEG normal | Same as ENV-001 | Same CC0 evidence | None required | OpenGL normal map. |
| ENV-003 | `polyhaven/clean_asphalt/2k/clean_asphalt_arm_2k.jpg` | 2048×2048 JPEG ARM | Same as ENV-001 | Same CC0 evidence | None required | Ambient occlusion/roughness/metalness packed map; channel interpretation must be checked in the material authoring tool. |
| ENV-004 | `polyhaven/qwantani_noon_puresky/2k/qwantani_noon_puresky_2k.hdr` | 2K Radiance HDR | [Qwantani Noon (Pure Sky)](https://polyhaven.com/a/qwantani_noon_puresky), Greg Zaal (photography), Jarod Guest (processing) | Individual page metadata identifies CC0 1.0; [Poly Haven license](https://polyhaven.com/license) | None required | 2K staging choice from a source with 24K maximum resolution; clear midday pure sky. |
| ENV-005 | `polyhaven/concrete_road_barrier/2k/concrete_road_barrier_2k.usdc` | 2K USD crate | [Concrete Road Barrier](https://polyhaven.com/a/concrete_road_barrier), Amal Kumar | Individual page metadata identifies CC0 1.0; [Poly Haven license](https://polyhaven.com/license) | None required | Valid USD crate. Page describes weathered concrete with chipped black/white checker paint; visual fit for the fictional Gujarat highway is unresolved. |
| ENV-006 | `polyhaven/concrete_road_barrier/2k/concrete_road_barrier_diff_2k.jpg` | 2048×2048 JPEG diffuse | Same as ENV-005 | Same CC0 evidence | None required | Barrier material map. |
| ENV-007 | `polyhaven/concrete_road_barrier/2k/concrete_road_barrier_nor_gl_2k.exr` | 2048×2048 OpenEXR normal | Same as ENV-005 | Same CC0 evidence | None required | OpenGL normal map. |
| ENV-008 | `polyhaven/concrete_road_barrier/2k/concrete_road_barrier_rough_2k.exr` | 2048×2048 OpenEXR roughness | Same as ENV-005 | Same CC0 evidence | None required | Roughness map. |
| REF-001 | `polyhaven/old_tyre/2k/old_tyre_2k.usdc` | 2K USD crate | [Old Tyre](https://polyhaven.com/a/old_tyre), Poly Haven | Individual page metadata identifies CC0 1.0; [Poly Haven license](https://polyhaven.com/license) | None required | Worn tyre reference only; not approved as a new spare wheel. |
| REF-002 | `polyhaven/old_tyre/2k/old_tyre_diff_2k.jpg` | 2048×2048 JPEG diffuse | Same as REF-001 | Same CC0 evidence | None required | Reference material map. |
| REF-003 | `polyhaven/old_tyre/2k/old_tyre_nor_gl_2k.exr` | 2048×2048 OpenEXR normal | Same as REF-001 | Same CC0 evidence | None required | Reference material map. |
| REF-004 | `polyhaven/old_tyre/2k/old_tyre_rough_2k.exr` | 2048×2048 OpenEXR roughness | Same as REF-001 | Same CC0 evidence | None required | Reference material map. |
| AUD-001 | `audio/blinker01.wav` | WAV, IEEE float, stereo, 44.1 kHz | [Car Blinker SFX](https://opengameart.org/content/car-blinker-sfx), OpenGameArt page; original uploader attribution is recorded on the source page | Page exposes CC0 license | None required | Downloaded filename preserved. Prototype only. |
| AUD-002 | `audio/blinker02.wav` | WAV, IEEE float, stereo, 44.1 kHz | Same as AUD-001 | Same CC0 evidence | None required | Prototype alternative. |
| AUD-003 | `audio/blinker03.wav` | WAV, IEEE float, stereo, 44.1 kHz | Same as AUD-001 | Same CC0 evidence | None required | Prototype alternative. |
| AUD-004 | `audio/door_closing.wav` | WAV, IEEE float, mono, 44.1 kHz | [Car Door SFX](https://opengameart.org/content/cardoorsfx), OpenGameArt page | Page exposes CC0 license | None required | Prototype door interaction sound. |
| AUD-005 | `audio/door_opening.wav` | WAV, IEEE float, mono, 44.1 kHz | Same as AUD-004 | Same CC0 evidence | None required | Prototype door interaction sound. |

## Not acquired

| Source | Decision |
|---|---|
| [Kenney Car Kit](https://kenney-assets.itch.io/car-kit) | Not downloaded. The source page was not retrievable in this environment, so its current individual license/package evidence was not archived. It remains a distant-traffic candidate only after visual-quality and license verification. |
| [Poly Haven tools/equipment](https://polyhaven.com/models/tools-equipment) | Not downloaded. This is a category, not an individual asset. Select and record individual jack/lug-wrench assets only when needed. |
| [Mixamo](https://www.mixamo.com/) | Not downloaded or integrated. Reserved for a later mechanic milestone; current account/product licensing and redistribution terms require review before shipping files. |
| Spare wheel, jack, lug wrench | Not created or acquired. Deferred unless vehicle inspection reveals a compatibility test need. |

## Integrity records

SHA-256 hashes for staged source/audio files and preview renders were recorded during staging. Hashes for the downloaded Poly Haven files should be regenerated and added here after any final conversion or normalization step. No conversion has been performed.

## Conversion status

No conversion has been performed. The preferred next pipeline is:

1. Inspect/author in Blender.
2. Export editable geometry as USD/USDC where possible.
3. Produce USDZ only for self-contained distribution after materials, scale, hierarchy, and animations are validated.
4. Import into Reality Composer Pro without maintaining a duplicate production scene definition.

