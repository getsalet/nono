# Generated images: staged restoration

Owner request: each active blog generator uses its own two image credentials,
model `agnes-image-2.5-flash`, and every newly generated post has 1–2 images.
The economical default is one fully reviewed image; a second unreviewed image
is never admitted. This does not edit already published articles.

| Blog | Image secret names |
| --- | --- |
| Roya | AGNES_API_KEY16, AGNES_API_KEY17 |
| Farsiblog | AGNES_API_KEY18, AGNES_API_KEY19 |
| Rozblog | AGNES_API_KEY20, AGNES_API_KEY21 |
| Loxblog | AGNES_API_KEY22, AGNES_API_KEY23 |
| Blogsky | AGNES_API_KEY24, AGNES_API_KEY25 |
| Parsiblog | AGNES_API_KEY26, AGNES_API_KEY27 |
| Niloblog | AGNES_API_KEY12, AGNES_API_KEY13 |

Text preferred slots 14/15 remain unchanged. When enabled, image-slot values
and aliases cannot be selected by the text pool. Actual secret values are never
read into reports or committed. Distinct names are not proof of distinct values
or image capability: validation checks duplicate runtime bindings and real bytes.

## Reference parity

Compared `blog_generated_image.py`, `blog_image_connection.py`,
`blog_reference_scene.py`, `blog_image_gate.py`, and `blog_image_watermark.py`
with `kapitansaman/afp-pipe` at
`bd0f30049a4429ea3d5a0a92f93a7fa2f9d2583f`: identical before these changes.
Retain its reference-conditioned product identity, article-specific scene,
no-people/wrong-product gate, landscape WebP, exact deterministic
`AFP | 09134922013` watermark, actual-pixel review and immutable asset URLs.
Existing practical score-90 policy and direct rejection overrides remain intact.
An illustration is not evidence of a real installation in a named locality.

## Deliberate rollout, not automatic publication

`data/blog-image-restore.json` is initially disabled. Legacy runtime behavior
continues until capability validation and an article-level image canary pass.
The pair-validation workflow is bounded to fourteen unique image calls, one per
assigned credential, and never publishes a post or enables production.
A durable request reservation prevents repeating the same request after a timeout.
A 402/429/quota or shared queue-full response stops the run instead of rotating
around a provider/account limit. Failures and missing/duplicate slots are not
reported as healthy. Real image bytes prove capability, not visual approval.

Before enabling: inspect the report, require the intended pairs to have real
image proofs, use the explicit seven-blog restore registry under the unchanged accepted family
and reference controls, and
run an article-specific generated-image canary with unchanged visual QA.
The routing gate requires matching completed pair evidence ≤72 hours old or a
real successful runtime generation by that previously proven slot within 72 hours.
Thus healthy ongoing publication does not require repeated paid capability probes.
Unused stale slots are not re-admitted without evidence. Missing/stale evidence
stops image work, never falls back to a text-only post.
Do not enable first and discover eligibility by failing production posts.

Blogfa stays retired. Hose-family holds/cancellations and all publication budgets,
independent text review, native/public verification and uncertain-intent handling
remain in force. Existing Niloblog static catalog reservations remain reconcilable;
new generated-image receipts do not consume unrelated catalog reservations.
