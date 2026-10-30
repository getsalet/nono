# Image calibration — 2026-10-30

## Production change

Commit `8d7a71806f3b660a41b1150628b05e990c7ce902` changes the shared tape image prompt and acceptance gate, not an individual article.

- Keep exactly one reference-conditioned, factory-closed AFP carton, with intact sidewall and no exterior attachments; structured scene evidence still comes from the actual article.
- Overall practical score >=90 is no longer sufficient: a separate focused review must explicitly return `package_has_protruding_strip: false`.
- Missing/invalid focused evidence does not approve an image. Old cached primary scores do not bypass this requirement.
- Other minor spacing/framing details remain advisory; wrong family, extra products, false branding, unrelated topic and other core defects remain blocking.
- Model, two-image-key-per-blog assignments, mandatory 1–2 images, default one, provider lock/cooldown, family holds and blog retirement settings were not changed.
- Image-conditioned finish edits remain diagnostic ONLY. They are NOT used by the production generator.

## Bounded live experiments (no blog publication)

1. [Baseline / first candidate](https://github.com/getsalet/nono/actions/runs/41028392857): baseline pictures retained white tails; the first tuned candidate removed the tail but duplicated the carton. A later generation stopped on `503 image_queue_full`; it was not treated as a visual rejection.
2. [Closed-carton prompt v2](https://github.com/getsalet/nono/actions/runs/41029742464): one output still had a tail despite an overall score of 96. The other had a single closed carton and no visible tail; its initial automated review was interrupted by HTTP429. Planned holdout/repeat cases did NOT execute and must not be counted as passes.
3. [Image-conditioned finish edits](https://github.com/getsalet/nono/actions/runs/41030647254): both edits removed the tails, but direct visual inspection found duplicated/overlapping contact stamps. These outputs were excluded despite primary scores of 93 and 96.
4. [Masked-reference finish edits](https://github.com/getsalet/nono/actions/runs/41031355848): masking the input stamp did not reliably preserve identity. Direct inspection found a changed dark base band and an extra background AFP mark in the first output, despite a score of 95. The second output was visually cleaner but its initial review failed with HTTP502; a later validation did not approve it. Its precise later rejection reason was not retained, so no cause is asserted.
5. [Existing-image validation with the deployed gate](https://github.com/getsalet/nono/actions/runs/41032184352): zero new image-generation requests. The native v2 output below passed the current primary gate with score 95 and the independent no-tail check. The edited output was not accepted. This is a limited sample, not a measured future success rate.

## Selected experimental sample

- Source: `artifacts/blog-image-calibration/41029742464/case-2-candidate-v2.webp`.
- Current validation: case 1 in `artifacts/blog-image-calibration/41032184352/report.json`.
- Primary score: 95; `closed_package_required: true`; `package_has_protruding_strip: false`.
- Direct visual inspection: one blue-and-white AFP carton, no loose white tail, no extra carton, one contact stamp. Small secondary package print is imperfect; the main AFP mark is recognizable. This is not a real-location documentary photograph.
- The sample was not inserted into or published as a blog post.

## Offline regression

The full local unittest suite passed: 1469 tests. Coverage includes no-tail fail-closed behavior, cached-score binding, preserved advisory spacing, product/topic contracts, reference-only stamp masking, and a final-validation harness that cannot call the image generator. Service errors are never counted as quality approval.

The diagnostic workflow is manual-dispatch only, bounded, and separate from blog publication. Review-only mode uses unreserved text-review credentials and never borrows another blog's image pair; duplicate slot 8 is not exposed in this diagnostic workflow.
