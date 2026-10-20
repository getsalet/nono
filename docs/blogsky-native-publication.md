# Blogsky native city-post publication

Blog: https://afp-pipe.blogsky.com

## Current operating mode

- Generation and export remain in `blogsky-content.yml`; `BLOGSKY_PUBLISH=0` is intentional there.
- `blogsky-native.yml` remains the manual diagnostic/single-post recovery path.
- Explicit user authorization enabled `blogsky-auto.yml`: hourly at minute 17 UTC (GitHub scheduling may be delayed), plus one immediate activation run. It generates at most one priority draft and publishes at most one current QA-approved article.
- Automatic mode enforces **one verified publication in a rolling 60 minutes**; held families, missing credentials and unresolved submission journals block the cycle.
- `data/blogsky/native-publication-control.json` now explicitly selects `automatic_one_post`, maximum one per run, with schedule enabled. The export adapter remains non-publishing by design.
- Default operation is `diagnose`: repository secrets authenticate, then the expected blog, native editor and management archive are checked. No AI generation or post submission.
- `publish-one` requires an explicitly selected city key and one existing completed, currently approved export. It does not generate another draft.
- Repository secrets: `BLOGSKY_USERNAME` and `BLOGSKY_PASSWORD`. Never place credentials/cookies in files, logs or artifacts.

## Manual sequence

1. Generate/review a single draft with the city generator; resolve QA failures before proceeding.
2. Run the native workflow in `diagnose` mode to confirm the repository connection.
3. Explicitly run `publish-one` with the approved `city-…` key.
4. Inspect the native-publication receipt and public post. A green generation/export run is not evidence of publication.

## Acceptance and recovery

The publisher revalidates the raw article, exact links, title, source-image provenance, current image/family policy and originality corpus. It then checks native editor serialization before submission. The native form retains the existing rich single-post wrapper.

Immediately before clicking Publish it saves a `submitting` journal. In automatic mode this intent must also be committed and pushed to `main` before the native click; a failed push prevents submission. A failure or missing public confirmation leaves an unconfirmed journal and blocks any further submission. Reconcile archive/public state; do not rerun blindly. Verified publication requires matching public title and article text, both exact contextual links, three native FAQs, the selected source image when present, footer and mobile call button. Only then are queue and publication history updated.

Already-published targets are idempotent. The rolling hourly budget is retained; this manual workflow adds a stricter maximum of one post per invocation. Global stop controls, held product families and Blogfa retirement are unchanged.

## First controlled acceptance

The first native post is the county-scoped Asadabad tomato needs-assessment article, key `city-373f12c4d2b81e25`. Its initial AI draft failed validation. The saved text was manually corrected without another paid generation call, passed full QA, and was submitted once through the authenticated native form. Public DOM readback verified its content, two contextual backlinks, three FAQs, source image and rich layout.

Receipt: `artifacts/blogsky-backlink-queue/native-publications/city-373f12c4d2b81e25.json`.

The native connection's repository-secret diagnostic is a separate acceptance test; the first public post alone does not prove unattended repository login. Automatic publication is operational only after the new workflow confirms login and public readback. Missing `BLOGSKY_USERNAME` / `BLOGSKY_PASSWORD` blocks before browser installation or login.

## Stop and recovery

To disable automatic publishing, replace the native publication control with the prior exact manual configuration (`enabled=true`, `mode=manual_one_post`, `max_count_per_run=1`, `schedule_enabled=false`), or use the existing global stop. The automatic workflow fails closed under manual configuration. Do not delete an uncertain journal or set it verified without checking the native archive and public article. GitHub logs/artifacts must never contain credentials, cookies or browser storage.
