# Observed generator run reports

`blog-run-report.yml` observes completed main-branch runs of the eight allowlisted workflows for seven active blogs. It never executes a generator, logs in to a blog, retries work, or changes scheduling, models, publication limits, retired providers, or quality gates. Blogfa is excluded.

Each report records the original run ID and attempt, final workflow conclusion, failed phase where available, a bounded cause category, generation outcome when a producer report matches the run, retry guidance (never authorization), and publication evidence limitations. Unknown causes stay unknown. No raw logs, error bodies, environment, or step outputs are copied.

Files:

- `artifacts/blog-run-reports/<blog>/latest.json`
- `artifacts/blog-run-reports/<blog>/<run-id>-<attempt>.json`

The observer reads Actions job/step results and the checked-out main snapshot. It records the snapshot SHA. Receipt timestamps overlapping a run are reported as **observed in the snapshot**, not proof that that run submitted them. Recovered receipts with unknown original publication time are excluded. The dashboard's total publication count continues to use the original receipt source, independently.

Latest reports advance monotonically by completion time, run ID, and attempt. Reports are written with a private Git index and report-only path allowlist; concurrent edits to the same report abort rather than overwrite. Concurrent changes to other blogs are preserved. Report artifacts remain available when a repository push fails.

If a workflow/job was skipped before its generator ran, the observer can record the overall outcome but must not invent a budget, admission, CAPTCHA, or quality cause. Missing observer reports are not equivalent to healthy or failed generators; the panel falls back to existing evidence. The observer is not a 24-hour independent public-site availability probe.

Manual verification: dispatch this observer with a completed generator `run_id`. This only collects a report; it does not rerun the referenced workflow. Avoid dispatching publication workflows merely to test reporting.
