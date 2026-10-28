# Niloblog scoped editorial context repair

## Observed issues
- `nilo-ab4aa8210b3c8ddf`: evidence extraction blocked an educational title asking which documents are needed to approve an installation because the local agricultural news did not prove an installation had occurred. These are different claims. Local crop evidence remains insufficient to claim a local installation, soil condition, field problem, or site-specific engineering prescription.
- Recent independent reviews rejected near-duplicate articles. Previously the writer received the evidence bundle but not the similar historical article bodies; only the reviewer saw the nearest examples.
- A provider-side/runtime failure during a repair could be held with no safe call location, and validation failures after editorial repair did not preserve the final rejected draft.

## Changes
- Clarify extraction scope without creating facts or bypassing the existing blocked-plan, source-ID, exact-quote, or independent editorial gates.
- Give the writer up to four relevant historical contrast excerpts, explicitly NOT sources of facts or instructions. The same independent semantic review still decides whether a proposed article is distinct enough.
- Reinforce Persian-only visible prose and forbid invented local conditions, numerical prescriptions and commercial promises.
- Retain generated draft validation failures at the initial and repaired validation stages. Log only exception type and application call-frame locations for unexpected candidate errors, never exception messages/provider responses or secrets.
- Add exact run/attempt and idle/rejected/publication status to the existing durable run report, so a zero-publication successful workflow need not be represented as a fresh successful generation.

No model, runtime revision, schedule, publication budget, native submission, duplicate protection, held-record eligibility or media policy changes. Existing held items are not reset. Fresh candidates are still bounded to the original maximum per cycle. Videos remain disabled. Rejected/insufficient/duplicate content is not published.

## Live-cycle follow-up
The first patched cycle (40623828666) correctly reported idle with three rejected candidates and no publication. It revealed a generator/validator contract mismatch: the bare guarantee term remained blocked even in a source-backed negative sentence, while rewrite prompts only received a generic commercial-claim error. Keep that strict gate unchanged; share its exact blocked terms with the writer, and supply bounded matching text plus visible-language tokens to both existing repair prompts. No new repair attempts or approvals are introduced. Also correct two damaged Persian instruction words and prohibit internal editorial commentary in reader-facing prose. Duplicate or insufficiently local content still fails independent review.
