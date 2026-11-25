# Graph viewport candidate, not Host accepted

Independent branch from 60317e8. The installed CDs candidate was measured as SHA256 421fdeadb89b06037dae64e6efb213b7ec8fe39e71983e9732b54092d69aec30. Its reported non-display was not reproduced: the inspected Resolve view had no selected PM effect and a disabled Settings tab.

Source inspection identifies a separate reproducible disappearance path: the overlay is suppressed when the visible image rectangle is small, even if the viewport has enough room. This candidate falls back to the viewport for zoomed-out, narrow portrait, offscreen, or invalid image bounds. It retains the minimum viewport threshold, Graph OFF early return, V1 registration, legacy GL state/glyphs and unchanged pixel pipeline.

Portable tests cover eight placement cases plus existing model/isolation checks. No Windows native OFX build, GL rendering, Resolve ON/OFF, export equality, or user acceptance is claimed. This is a candidate, not a confirmed fix of the owner's observed symptom.

Next Host gate: preserve the existing project and rendering state; use an independent test project, select an actual PM OFX instance, confirm overlays enabled, compare Graph ON/OFF and small/large image zoom. Export identical settings with Graph ON/OFF and compare decoded RGBA. Do not replace the currently installed binary before a new Windows build and preservation.
