# Bilingual package-caption calibration — 2026-10-30

## Requested canonical captions
- Beneath AFP: `Drip Irrigation Tape`.
- Beneath blue water-drop symbol: `آبگسترفراپاریان`.

## Scope and production state
The experimental renderer is committed under `automation/blog_package_labels.py` and is called by the manual no-publication calibration workflow only. It is **not enabled or connected to production preparation**. No article queue/state or post submission was changed by these calibration scripts. Existing image model, per-blog key allocation, provider backpressure and held product families are unchanged.

## What changed in the experimental shared renderer
- Automatic local AFP glyph/band/symbol anchors; no per-article coordinates.
- Deterministic English and joined RTL Persian typography in two small sleeve regions.
- Hash-pinned bundled Noto fonts, with license and notice; same typography on local Linux and GitHub Ubuntu.
- Cleanup before both text layers; no product-photo replacement or model-based logo redraw.
- Original AFP glyph/symbol blue pixels and phone watermark protected by regression checks on four real frames.
- Blind literal transcription, without either expected caption in the reader prompt; full frame, enlarged detail and separate perspective-rectified caption views.
- Exact text comparison remains fail-closed. A high overall image score cannot excuse incorrect/missing caption transcription.

## Live backtest evidence
| Run | Change | Result |
| --- | --- | --- |
| [41036152601](https://github.com/getsalet/nono/actions/runs/41036152601) | First blind-source inspection | HTTP 502 before a new generation; not approval. |
| [41037090356](https://github.com/getsalet/nono/actions/runs/41037090356) | Local geometry, existing frames and one unseen native holdout | Existing baseline and holdout blocked by protected-pixel collision under different CI fonts. Other angle rendered English correctly but Persian transcription failed. None accepted. Exactly one new image request received HTTP 200; zero post submissions. |
| [41038504803](https://github.com/getsalet/nono/actions/runs/41038504803) | Pinned fonts, unified cleanup, enlarged blind readback | All three captions rendered locally without mark collision. English read exactly in all three; Persian missing/mistranscribed. **0/3 accepted**. No new image generation or post submission. |
| [41039103424](https://github.com/getsalet/nono/actions/runs/41039103424) | Separate rectified caption-only views, no spelling hints | English read exactly in all three; Persian still mistranscribed (آبگستر فرایران / آبگستر فراپایان / آبگستر فرایارسان). **0/3 accepted**. No new image generation or post submission. |

Complete reports and candidate bytes are in `artifacts/blog-image-calibration/<run-id>/`.
The actions job reporting success means the bounded diagnostic completed and saved its report, **not** that its images passed.

## Offline evidence
- 14 caption tests pass: literal comparison, blind prompt, Raqm shaping, geometry/homography, four real frames, exact protected-logo pixels, unchanged watermark, cache binding, invalid policy, quality-vs-runtime failure separation.
- Full existing suite plus initial nine caption tests: **1478 passed**.
- A locally prepared (not deployed) production-integration candidate with five additional caption safety tests: **1483 passed**. This does not establish live visual approval or production activation.
- Visual inspection of full holdout and three enlarged details showed correctly typeset canonical strings; this is useful local evidence, not a substitute for the failed independent automated acceptance condition.

## Remaining blocker
The independent blind reader does not reliably transcribe the complete small Persian company name at the current scene scale. Do not replace its answer with expected text, mark the samples passed, disable the exact-text condition or activate the unvalidated production hook. Revisit final scene-scale lettering size/placement or independent OCR capability in a separately bounded calibration. Tiny old secondary print in the low-resolution original packshot is not authoritative for the new Persian wording; the user's explicit spelling above is authoritative.

A two-line company-caption layout was also tried offline, but one angle collided with protected ink. It was not committed or activated; the committed output remains single-line branding.
