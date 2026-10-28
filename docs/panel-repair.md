# Targeted repair from the public status panel

The panel links to an authenticated GitHub Actions `workflow_dispatch` form. The user supplies the displayed exact `blog` and `target`, chooses `repair` and types `REPAIR`. A link click alone never performs a write. No token, OAuth credential, or provider secret is stored in Pages. `inspect` only checks eligibility.

Supported real repairs:
- **Parsiblog pre-submission text QA failure:** use the existing generator's rejected-draft feedback loop for that same approved title, then rerun text QA, independent editorial review, image review, and final QA. Persist the repaired **ready** item only when approved. This workflow never invokes a native draft/publication mode. Ordinary schedules can subsequently publish the ready item under their original guards. A rewrite can still fail QA; that is reported as a failed repair, not success.
- **LoxBlog unresolved submission:** locate the unique existing native post and verify its public body against the saved approved article, then restore its receipt and queue checkpoints. Never resubmit or create a post. Missing/mismatched posts remain blocked.

No repairs for Blogfa, held/cancelled families, paused automation, unknown causes, missing approved evidence, or authentication problems. No quality/budget/model/schedule changes. Production article model stays `agnes-2.5-flash`; Niloblog video policy is unchanged.

Both repair operations share the original production concurrency lock, checkout latest main under the lock, and revalidate target eligibility. One repair attempt is consumed per exact failure-state fingerprint. A failed attempt requires investigation, not another button click. If checkpoint push conflicts, the job fails and retains an artifact; never assume the local repair is persisted. Native uncertain writes are not repeated.

Results: `artifacts/panel-repairs/<blog>/latest.json`, per-target attempt marker, authenticated run summary and artifacts. The public panel labels draft repair separately from receipt recovery and inspection. It shows target and observation time so an older result cannot masquerade as the outcome for another item. Reports contain allowlisted identifiers and application-authored reason codes, not raw exceptions or private logs.
