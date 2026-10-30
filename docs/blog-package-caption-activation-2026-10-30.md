# Approved caption production activation

Owner explicitly requested applying the approved cylindrical lettering after correcting the company name to **آبگسترفراپارسیان**. English remains **Drip Irrigation Tape**.

## Applied scope
- `blog_generated_image.prepare_now` invokes the shared cylindrical `prepare_cached` renderer after native generation/cache retrieval, before local QA and immutable asset checkpointing. It runs outside the image provider's FIFO lease.
- `require_exact_package_labels: true` is enabled for tape20 only. The approved renderer uses the measured blue-band curvature and hash-pinned fonts. Caption policy is included in tape asset identity, so old garbled assets cannot masquerade as newly approved caption output. Hose identity is unchanged.
- The native art direction requests a clearer, near-frontal sleeve at about one third of frame width, and uses the canonical company spelling. No source-product replacement or model-based logo redraw was added.
- Generation records include caption policy and render provenance. Primary vision QA knows that the exact owner-specified company wording is genuine; the separate blind reader is NOT given either expected string.
- Existing cached primary scores cannot bypass the new independent, hash-bound literal-caption check. Caption proof must match policy and actual encoded image bytes; old spelling, missing text, or unreadable transcription does not pass.

## Failure and cache handling
Definitive local layout or main-image defects retain the existing bounded rejection/regeneration path. Runtime/font/provider failures do not become image-quality rejections. Unresolved literal OCR is pending verification, not proof that native generation is wrong: the already-rendered candidate and typography sidecar are retained, no extra image request is spent merely for this uncertainty, and no publication is authorized. The stock worker uses its existing per-item retry backoff; no new global provider hold is set. Successful checks are reused only for matching image SHA and current policy.

## Preserved controls
No image model, per-blog two-key assignment, image-count policy, schedule, shared provider cooldown/locking, held family, retired blog, existing article, published post, or historical immutable public image was changed. Current source code/config apply on subsequent runs that load main; this activation does not itself submit posts or claim that an already-running job has refreshed its checkout.

## Validation and limits
Four offline production-wiring tests cover real local typesetting before QA/checkpoint, retained candidates without regeneration for OCR uncertainty, rejection of stale high-score approval without literal readback, and tape-only activation. Provider and vision transports are mocked in these tests; the watermark presence check is isolated only in the cached-review test, not changed in production. Existing caption geometry tests retain original logo/symbol and watermark pixel checks.

The complete offline suite passed **1492 tests**, including 19 typography tests and 4 activation tests. No new live provider image, independent online OCR approval, or successful blog publication is claimed by this activation. The earlier live Persian-readback limitation remains a potential publication blocker; it has not been bypassed or silently treated as success.
