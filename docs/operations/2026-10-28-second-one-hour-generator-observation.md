# Second one-hour generator observation — 2026-10-28

Window: 08:36:32–09:36:32 UTC. This is a separate observation window, not continuous monitoring since the earlier 05:55–06:55 window.

## Foundation changes
- e2092e05d19ed4c3a9a71afabd233e4d37dbe2b5: render standalone AFP_CITY in visible prose/meta/tags from the exact approved matrix locality before QA. Do not guess translations or rewrite URLs, slugs, assigned titles or unrelated prose. All 1000 approved matrix rows passed rendering checks.
- ef236000f9e9fb1fe7db51f6c60b983f64c9521a: wait up to 10 seconds for the same strict native LoxBlog management identity; recheck route and exact expected link. No navigation, credential resubmission or publication in this wait. Failure diagnostics contain only fixed boolean categories. This is resilience and diagnosis; an original rendering race was not conclusively proven.
- 1c9cf51113807cee63d4bbc7e58cdffe25d89eb1: when the only remaining static error is foreign-language text, use exact visible-token repair instead of regenerating a whole otherwise-valid article. At most eight identified edits, Persian-only replacements of at most four words, no markup/digits/URL edits or valid Persian word edits. Keep the existing three-attempt ceiling. Unknown patches fail closed. Preserve before/after digests and edit counts; rerun complete static, independent editorial, image and native/public verification gates.

## Real outcomes
### Parsiblog
- Initial run 40653967991 rejected mixed-script place name before any native write.
- First fix test 40659069608 still rejected another foreign word, Russian “или”; city templating alone was insufficient. No native write occurred.
- Successful controlled run 40661937348 used an exact one-token edit “или” → “یا”, passed independent review and complete QA, generated one image, and publicly verified post 49/native ID 8028245 at 09:14:02 UTC. Saved item contains the exact language-repair manifest. 710 Persian word groups and three approved links.
- A separate scheduled run 40660338028 held a different draft for editorial claims. That hold was not reset or mislabeled as an infrastructure outage.

### LoxBlog
- Original run 40654063379 made one native submit and left city-cc8ebde2c12e4930 unconfirmed after a management-identity check.
- First existing-only recovery 40658578842 stopped before credentials were submitted because the visual-challenge service timed out. No duplicate POST.
- Public read-only comparison found the observed exact-title article and confirmed full approved text, one matching image, three FAQs and no comment form; this evidence alone did not release the native hold.
- Recovery 40661957260 verified the existing native/public post 75 and changed the journal to verified with new_submissions=0. Do not count this as a newly submitted article or use recovery time as proof of original publication time.
- Interim green LoxBlog runs 40659547227 and 40660358666 were protective reconciliation-blocked checks, not evidence of new publication.

### Other observations
- Blogsky run 40658601184 verified post 38 and six homepage image cards. Cover synchronization used zero article submissions.
- Roya receipts recorded post 618 at 09:18:22 UTC; publication run 40662940607 completed successfully.
- Niloblog report at 08:31 remained idle with three evidence/topic holds and no pending intent; no new Niloblog publication was claimed from this report.
- Farsiblog run 40662013859 completed successfully and recorded verified post 305 at 09:33:28 UTC. Its generation report was partial_success (two completed, two rejected), not a claim that every draft passed.
- Rozblog run 40662028051 completed successfully and recorded verified post 329 at 09:31:44 UTC. Its generation report was partial_success (two completed, three rejected). The earlier 403 was not reproduced by this successful native publication; this does not guarantee the external service will never deny access again.
- Niloblog successor run 40664497996 completed with idle, three evidence/topic holds, zero generated articles and no pending intent at 09:30:29 UTC. These drafts were not released by weakening evidence gates.

## Tests and observation integrity
- Final full offline suite: 1276 tests passed. Parsiblog targeted suite: 100 tests passed; LoxBlog targeted suite: 56 tests passed before the later Parsiblog-only change.
- Exact generation-language gates, image identity/review, public-content matching, duplicate/uncertain-submit holds, family scope and rolling publication budgets remain active.
- Observed both authenticated rendered Actions and a bounded public Actions API watcher, without putting tokens or passwords into page code or artifacts.
- Raw main-branch file reads were found stale despite cache-busting query strings. Subsequent evidence snapshots were read at the observed immutable main commit SHA. Prefer immutable snapshot URLs when interpreting this report.
- Historic red runs remain red; successful successor runs and durable receipts demonstrate the repairs.

## Completed window and final snapshot
- Window completed: 2026-10-28T09:36:32.037037+00:00. Final Actions API observation: 2026-10-28T09:36:32.037173+00:00.
- Immutable final repository snapshot: `6ee8e8ce0d022de5e7af740d490e9b3068adcb5e`.
- The rendered-browser observer stopped at 08:59 after its page/context was closed; the independent API observer was already active and continued periodic observations through the exact window end. No claim of continuous browser observation is made.
- At window end, Roya generation run 40665386321 was still in progress. No outcome is claimed for it. The monitor stopped at the end of this window; it is not ongoing.
- No secrets, session exports or native resubmissions of uncertain posts were used.

### Evidence
- [Successful Parsiblog foundation test and post 49](https://github.com/getsalet/nono/actions/runs/40661937348)
- [LoxBlog existing-only recovery, post 75, zero new submissions](https://github.com/getsalet/nono/actions/runs/40661957260)
- [Blogsky normal generation, publication and homepage covers](https://github.com/getsalet/nono/actions/runs/40658601184)
- [Farsiblog normal cycle](https://github.com/getsalet/nono/actions/runs/40662013859)
- [Rozblog normal cycle](https://github.com/getsalet/nono/actions/runs/40662028051)
- [Niloblog bounded evidence/topic holds](https://github.com/getsalet/nono/actions/runs/40664497996)
- [Final immutable Parsiblog report](https://github.com/getsalet/nono/blob/6ee8e8ce0d022de5e7af740d490e9b3068adcb5e/artifacts/parsiblog-backlink-queue/run-report.json)
- [Final immutable LoxBlog recovery report](https://github.com/getsalet/nono/blob/6ee8e8ce0d022de5e7af740d490e9b3068adcb5e/artifacts/loxblog-backlink-queue/existing-receipt-recovery.json)
