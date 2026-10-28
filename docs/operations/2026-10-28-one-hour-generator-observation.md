# Repository observation and foundation repairs — 2026-10-28

Observation window: 05:55:02–06:55:02 UTC (60 minutes). Final rendered Actions observation: 2026-10-28T06:55:02.567Z.

## Foundation changes
- 953454646e2be29d7e86a0b202ebaab571efe809: restore runtime Blogsky hosted image queue wiring and Actions read permission; one bounded second image candidate only after definitive visual rejection; safe Parsiblog pre-submit diagnostic codes. Transport/quota errors do not authorize regeneration or resubmission.
- d1840ab2a49fe15f803be5c61e3a3bb6680d16c6: regression tests for two-candidate ceiling and no 429 visual retry.
- 138ef076a0e5b4497ca6204eb437cea7410db5e3: homepage covers accept exact immutable same-repository Blogsky image assets only; existing content and verification gates retained.
- af93037564772f562d9e84641c25b69bd2e5a2aa: install complete offline test dependencies for shared queue verification.
- 5391ad1caf86530a10cbf58bcb1ce8fba4670030: classify missing claim/invalid source schema as topic holds, not infrastructure outages; missing claims still rejected, unknown exceptions still stop.

## Observed outcomes
- Parsiblog run 40641472006: published and publicly verified post 48, one generated image.
- Loxblog recovery 40641755474: existing post 73 verified, zero new submissions. Normal run 40641799804 subsequently recorded post 74 at 06:20:45 UTC. Two generation candidates failed checks; a green workflow is not proof all candidates passed.
- Blogsky run 40641456193: post 35 verified; later cover synchronization failed. Cover-only repair 40643283158 verified six covers, zero article submissions. Subsequent normal scheduled run 40645533038 completed, recorded post 36 at 06:49:28 UTC and verified six homepage covers at 06:49:43 UTC.
- Shared queue cross-runner verification 40643598609 passed, no image API calls.
- Niloblog test run 40645603412 completed: idle, three evidence/topic holds, zero generated/published articles, no pending publication intent. This is correct rejection handling, not proof of new publication.
- Farsiblog state recorded post 301 at 06:31:25 UTC; run 40643195005 completed.
- Roya state recorded post 614 at 06:29:47 UTC. Generation run 40642420442 produced three articles; publication is separately evidenced by receipts.
- Rozblog run 40643310402 generated two candidates successfully and rejected three; native publication stopped because /usercp.php returned 403 Access Denied. No security bypass or blind credential/publication retries were attempted. External native-panel access remains unresolved; inspect authorized panel access before another publication attempt. Do not label this an image-generation failure.

## Validation and limitations
- Final full offline suite: 1252 tests passed; targeted Niloblog suite: 151 tests passed.
- Historical failed Actions runs remain red; subsequent successful runs and durable receipts are the repair evidence.
- Not all held content should be released: source, language, identity, visual, duplicate and public-verification gates remain active.
- Public API rate limit occurred during the window; observation continued using authenticated rendered Actions and fresh public raw report files. An Actions DOM heading change briefly broke row extraction; selector was corrected from h3 to h3/h4. No continuous-observation or all-green guarantee is implied.
- Observation ended at the stated window. No ongoing monitoring is promised by this report.
