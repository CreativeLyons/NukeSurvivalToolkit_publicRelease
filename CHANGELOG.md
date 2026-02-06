# Changelog

All notable changes to the Nuke Survival Toolkit are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

**Tools (gizmos and Python)**

**2025**
- AnamorphicLensBlur (XM)

**2024**
- aeShadows (AE) v1.0
- FastComplexity_Distort (X_Distort)
- fxT_ChromaticAberration (fxT) v3.1
- Emission (NW) v1.2
- aeRefracTHOR (AE) v1.0
- LightSwitch (TL)
- LightSwitchPuppet template
- ChromaSmear (LJ)
- apEdgeCrush (AP)
- MirrorDimension (TL)

**2023**
- PointCloudKeyer (IS)
- SpotLight (TL)
- Rings of Power (TL)
- Symmetry (TL)
- SkyMatte

**2022**
- CardToTrack (AK) updated to v8.0 with NST_cardToTrack.py
- ID_Extractor (TL) with NST_ID_Extractor.py
- ConstantPro (TL)
- HexColor (NW)
- RadialDilate (CF)

**2021**
- GuidedBlur (RF)
- iErode (PP)
- aeRelight2D (AE)
- iTransform_ae (AE) — later fixed onCreate code for render farm
- ImagePlane3D_v2 (TL) v2.0
- bm_OpticalLightwrap (renamed from bm_Lightwrap)

---

**Other**

- `LOAD_EXPRESSION_MENU` configuration option in `menu.py` to optionally enable or disable the Expression Nodes AG submenu (default: disabled).

### Changed

- Icon assets recompressed for ~53% size reduction (~127 KB saved); no visual changes.
- `ColorGradientUi.py` updated for Nuke 16+ compatibility and PySide6 migration (GradientEditor MHD).
- Menu refactor: `nk_path()` and `icon_path()` helpers, f-strings, improved readability; no user-visible behavior change.
- Documentation menu now uses a `Documentation` submenu with `Wiki/Docs (Auto)`, `Wiki (Online)`, `Wiki (Offline)`, and `Docs (PDF)` commands. The auto command now falls back in order: online wiki -> offline local wiki -> local PDF, with reachability checks and concise missing-target guidance.
- Added dedicated icons for documentation submenu entries (`wiki_default`, `wiki_online`, `wiki_offline`) and used Nuke native `StickyNote` for PDF.
- `README.md` now includes an optional offline documentation install section that points users to release ZIP downloads and the required local path (`NukeSurvivalToolkit/NST_Documentation/index.html`).
- Updated .nk templates: NST_AdvancedKeyingTemplate_Stamps.nk, NST_X_Aton_Examples.nk, deepThickness.nk.
- New icon assets for aeRefracTHOR, aeShadows.

**Updated Tools**

*Nuke 13 compatibility:*
- aPCard
- AutoCropTool
- DeepKeyMix
- FrameFiller
- GlobalCTRL
- GradMagic
- ImagePlane3D
- LumaGrain
- Matrix4x4_Inverse
- mScatterGeo
- origami
- PlanarProjection (also fixed XAton volumes example)
- Reconcile3DFast
- Relight_Simple
- ReProject_3D
- RotoCentroid
- RP_Reformat
- Sparky
- SSMesh
- viewer_render
- VoronoiGradient

*Other updates:*
- apeGlow (fixed overscan bug on crop knobs)
- apChroma (internal restructure)
- apChromaMergeNew (internal restructure)
- apDespill_v2 (internal cleanup)
- apVignette (v0.5: added transform tab, "Apply to White Constant" option)
- bm_CameraShake (updated to v4.0)
- bm_OpticalGlow (updated to v4.1)
- CameraNormals (updated DummyCam to v1.3)
- CellNoise (fixed onCreate center calculation)
- ColorSampler (added option to export constant)
- DeepRecolorMatte (bug fixes, ported later version)
- DummyCam (v1.3, Nuke 13/14+ Camera3 class)
- ExponGlow (fixed bug that deleted luma key when changing iterations)
- Glass (added channel support and mask input)
- InjectMatteChannel (exposed bbox knob)
- LightWrapPro (fixed bounding box in non-final view modes)
- MorphDissolve (added 0→1 / 1→0 options, STmap export)
- SimpleSSS (internal cleanup)
- SliceTool (code cleanup)
- STmapInverse (code cleanup)
- Suppress_RGBCMY (added mask and mix features)
- UV_Map (fixed overscan scaling bug)
- UV_Mapper (internal cleanup)

### Removed

- `h_Qt.py` — obsolete Qt compatibility shim (no longer needed after PySide6 migration).
- `NST_bm_Lightwrap.gizmo` — replaced by bm_OpticalLightwrap.

### Fixed

- Windows filepath issues: use `Path.as_posix()` for all toolkit paths so forward slashes are used on every platform, avoiding backslash escape sequences (e.g. `\n` in `\nk_files`) that broke `nuke.nodePaste()` and file knobs on Windows.
- Help documentation link on Windows: use `Path.as_uri()` for the documentation PDF URL so drive-letter paths open correctly in the browser.
- Documentation online reachability check now handles environments where Python SSL certificate validation fails, preventing false fallback from online docs to PDF.
- Node class check in `filepathCreateNode`: use tuple membership instead of chained `or` for file-node detection.
- Replaced bare `except:` clauses with specific exception handling (ImportError, RuntimeError) for ColorGradientUi, VectorTracker, and NST_cardToTrack imports.
- Issue #43: menu and helper module loading.

---

## [2.1.1] - 2021-05-19

### Changed

- Updated NST_ImagePlane3D, NST_apDespill_v2, NST_FrameHoldSpecial gizmos.
- Updated deepThickness.nk script.

---

## [2.1.0] - 2021-04-28

### Added

**Tools (gizmos and Python)**

**2021**
- BokehBuilder (KB)
- LensEngine (KB)
- RankFilter (JP)
- MotionBlurPaint (AG)
- RotoPaintTransform (AG)
- Deep2VP (MJT)
- DVPColorCorrect (MJT)
- DVP_Shader (MJT)
- DVP_ToonShader (MJT)
- DVPrelightPT (MJT)
- DVPortal (MJT)
- FrameHoldSpecial (AG)
- InverseMatrix33 (MJT)
- InverseMatrix44 (MJT)
- apDespill v2 (AP)
- MonochromePlus (CF)

**2020**
- iMorph v2 (AP)
- LabelFromRead (TL)
- Unify3DCoordinate (MJT)
- SceneDepthCalculator (MJT)
- DasGrain (FH)
- Looper (DB)
- HeatWave (DB)

---

**Other**

- New documentation.

### Changed

- NST_ImagePlane3D, NST_GradMagic, NST_iMorph updates.
- Menu structure updates.

---

## [2.0.0] - 2021-03-29

### Added

**Tools (gizmos and Python)**

**2021**
- GodRaysProjector (CF)
- MonochromePlus (CF)
- RainMaker (MR)

**2020**
- ImagePlane3D (TL) v2.0
- FrameFiller (MJT)
- Edge (RB)
- Reconcile3DFast (DR)
- GlueP (LS)
- AutoFlare2 (NKPD)
- DeepMerge_Advanced (BM)
- bm_MatteCheck (BM)
- bm_NoiseGen (BM)
- bm_Lightwrap (BM)
- SimpleSSS (MHD)
- KeyChew (NKPD)
- AdditiveKeyerPro (TL)
- apeGlow (AP)
- iBlurU (NKPD)
- DeepFromDepth

---

**Other**

- ReadGeo class support in NST_helper.
- PerspectiveBB reset points button.
- UV_Map, injectChannelMatte tab rename.
- Menu restructure and submenus.

### Changed

- Nuke 13 compatibility updates across multiple gizmos.
- Major init.py restructure.
- Documentation updates.

### Fixed

- ImagePlane3D crop1, DirectionalBlur CopyBBox, bm_MatteCheck grey_amt.
- Menu bugs.
- NST_Reconcile3DFast.

---

## [1.1.1] - 2020-10-05

### Changed

- Updated NST_AutoFlare2 gizmo.

---

## [1.1.0] - 2020-10-04

### Added

**Tools (gizmos and Python)**

- AutoFlare2 (NKPD)
- FrameFiller (MJT)
- Edge (RB)
- Reconcile3DFast (DR)
- GlueP (LS)
- DeepMerge_Advanced (BM)
- bm_MatteCheck (BM)
- bm_NoiseGen (BM)
- bm_CurveRemapper (BM)
- bm_Lightwrap (BM)
- SimpleSSS (MHD)
- KeyChew (NKPD)

---

### Changed

- Dev branch merge; bm_Lightwrap replaced prior NST_bm_Lightwrap; various tool updates.

---

## [1.0.1] - 2020-09-26

### Changed

- Sparky DB updated to v1.5.
- README updates.

---

## [1.0.0] - 2020-09-23

### Added

**Tools (gizmos and Python)**

- Initial curated gizmo collection.

---

**Other**

- Portable tool menu for Foundry Nuke.
- Installation via init.py plugin path.

[Unreleased]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/compare/v2.1.1...HEAD
[2.1.1]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/compare/v1.1.1...v2.0.0
[1.1.1]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/CreativeLyons/NukeSurvivalToolkit_publicRelease/releases/tag/v1.0.0
