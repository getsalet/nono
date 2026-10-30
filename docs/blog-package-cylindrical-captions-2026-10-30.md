# Corrected company name and cylindrical sleeve typography

## Current wording
- Beneath blue water-drop: **آبگسترفراپارسیان**.
- Beneath AFP: **Drip Irrigation Tape**.
The previous آبگسترفراپاریان is obsolete and explicitly rejected by a regression test. The new policy identifier invalidates old caption proofs.

## Curvature correction
Both shaped caption layers now follow a nonlinear front-cylinder arc, not just a tilted plane. Curvature is measured from three robust symmetric samples of the actual blue band's top edge. Camera tilt cancels in the second difference. No article-specific coordinates or arbitrary decorative arc is used. Joined Persian bends as a single layer. Unsupported or excessive bending fails closed.

Three existing real-image cases rendered successfully. Measured center-to-chord sag in English/Persian: holdout 7.23/2.41 px, baseline 5.83/1.87 px, alternate angle 6.38/1.99 px. Visual inspection covered all three full frames and all three enlarged details. Original AFP glyph and symbol blue pixels, and watermark region, remain unchanged before final lossy WebP encoding. Scene, logo and product silhouette were not redrawn.

## Evidence and reproduction
Run `python automation/calibrate_curved_package_labels.py` from the repository root. This local-only helper uses existing images; no provider requests, post submissions or queue mutations.

Report: `artifacts/blog-image-calibration/cylindrical-faraparsian-v2/report.json`. It records source paths, output hashes, exact strings, fonts and measured curvature. A representative full-frame preview is stored alongside as `holdout.webp.b64` (base64-encoded WebP).

**19 caption tests and 1488 total offline regression tests passed.** New coverage includes current spelling, old spelling rejection, measured curve sign, unsupported flat-band rejection, nonlinear warp and excessive-bend rejection.

## Production state and limits
**Experimental only; not connected to production generation or activated.** No live image/OCR review was performed for this update. The earlier independent Persian readback problem is not claimed resolved. Small scene-scale type remains a readability limitation. Existing image model, image-key allocation, locks/cooldowns and held families are unchanged. The shared experimental renderer and diagnostic prompt were updated, not just one article image.
