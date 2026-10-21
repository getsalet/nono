# Parsiblog city generator

- Account/blog: AFP, http://afp.parsiblog.com/ (provider currently uses HTTP).
- Login secrets: PARSIBLOG_USERNAME, PARSIBLOG_PASSWORD. Existing AGNES text/vision keys are reused. No credentials are stored in files or artifacts.
- Inventory: 1,000 distinct assigned titles across 802 source city/locality labels, based on actual site target pages. Eight titles use approved county/municipality cultivation evidence. Other titles are crop-free: missing evidence never turns into invented local cultivation or agronomic advice. The source registry retains original locality labels; route/province aliases are not treated as agronomic evidence.
- Exactly three contextual links: main site, corresponding city product page, matching product category. Exactly one occurrence each, assigned anchors, no links in FAQs. Shared existing two-link generators are unchanged.
- SEO checks: title 12–65 chars; independent 500–1,000 Persian words; description 70–180 chars in export; 1–6 native tags under 120 chars; headings/checklist/conclusion; three final FAQ questions; actual product photo approved by the scoped real-photo vision gate; cross-blog and own-queue reuse rejection.
- Platform-specific FAQ format is h3+p because the native TinyMCE editor strips details/summary. Native source readback and public body verification check text, three links, headings, FAQ structure and image. Description/slug remain in export: no native per-post meta-description/slug field was observed, so their persistence is not claimed.
- No retries of ambiguous writes. A pre-submission checkpoint survives failure. Known draft IDs are updated rather than creating a second article. Uncertain results are reconciled by native title/body; if inconclusive, human review is required.
- Workflow: .github/workflows/parsiblog-content.yml. `probe` verifies secret-backed login only; `draft` saves and re-reads a real approved article without public release; `publish` promotes/reconciles one approved item and verifies the actual public URL; `generate` only exports; scheduled jobs are disabled until a public canary is verified.
- Publication ceiling: two verified posts per rolling hour, with workflow concurrency and the existing global stop respected. A successful public canary enables scheduled half-hourly runs only when control.activate_after_verified_canary is true.
- Publication receipts, draft IDs and errors: state/parsiblog-progress.json; artifacts/parsiblog-backlink-queue. No screenshots, DOM dumps, cookies or authentication state are uploaded.
- There is no guarantee of search-engine rankings. Articles must remain independently useful and evidence-bound, not doorway pages with fabricated local facts.

- Factual safety v2: unreviewed city-page prose is not fed to the model as evidence. Only approved scoped cultivation existence is supplied. Numeric technical prescriptions, chemical cleaning and fabricated local soil/water/product construction claims are rejected; an additional editorial model review must approve each text before image/native submission. Approval is bound to the exact saved post digest and rechecked before publishing.

- User-requested ceiling: 2 posts per rolling hour; cron at minute 23 and 53. A corrected canary seed is unapproved input only and must pass all deterministic checks, independent editorial review, image review and native/public readback. It never bypasses quality gates.

- Native form uses Windows-1256 responses; the adapter decodes the declared charset. The new-note `?Post` view does not contain the full notes list, so reconciliation uses Notes.aspx. Persisted titles may drop ZWNJ; only that explicit alternative and Arabic/Persian letter normalization are accepted, never changed words or locations.

- Internal native database IDs differ from blog-local public post ordinals. Public verification finds the unique exact normalized title, follows the actual rendered permalink and checks the complete body, image and three destinations; it never constructs a public URL from the internal ID.

## Reliability repair
- Application-owned contextual linking: the generator supplies Persian prose; code inserts exactly the approved home, city and category anchors in distinct body paragraphs before FAQ. Missing and duplicate approved links are repaired before strict QA and editorial review. Unknown destinations remain rejected; the three-link gate is not weakened.
- The last rejected JSON may be reused only as unapproved input to full deterministic, editorial, originality and image review. Explicit `--retry-pre-submit --target pb-...` can recover known pre-submission QA failures, never uncertain writes or published posts. The old failure remains in the state audit history.
- Every run writes its own run-report.json with run ID, status, phase and safe errors; the Actions summary refuses to display an earlier successful receipt as the current result.
- Event mode/target are captured first; latest main code and receipts are then refreshed under the shared publication lock, avoiding stale queued-run state. Existing global stop and the two-post rolling-hour ceiling stay in force.
- Public verification retries only read-only GETs, three bounded attempts. Native writes remain one-shot with checkpoint/reconciliation protection.
- Cron is every 30 minutes (minute 23 and 53), but GitHub may start scheduled runs late. This is a maximum publication frequency, not a wall-clock delivery guarantee.

## Real-product-photo scope
- Parsiblog is not enrolled in the generated-field-scene rollout. It uses the official canonical AFP product photograph, not an invented local farm image or dealer-branded warehouse photo.
- parsiblog_images.py requires fresh pixel inspection for its own policy/scope and a score of 90–100 with exact product identity, recognizable authentic AFP branding and every safety flag cleared. Missing farm soil, installed irrigation and generated-image phone watermarks are not defects in a real product packshot. Generated-image rules and other providers are untouched.
- Review records are stored separately under artifacts/parsiblog-backlink-queue/real-product-reviews. Shared rejected verdicts are neither overwritten nor treated as approvals. Current image bytes, manual visual rejection, global pause and held/cancelled families remain enforced.
- Approved text is checkpointed before image work. A retry treats it only as input to full QA and independent review. Failed pre-write runs may be explicitly recovered only with a matching timestamp-bound report proving no native write, or a known preflight failure; ambiguous and published states are never reset.
- Held product families are excluded before generation; explicit held targets stop without generation or login.

- Observed native persistence maps U+FF0C (fullwidth comma) to ASCII comma. Body readback accepts only this explicit punctuation equivalent in addition to existing Persian letter/whitespace normalization; all other word, destination, image and FAQ changes still reject. An acknowledged submission is reconciled/read back by ID and actual public URL without another create/save.
