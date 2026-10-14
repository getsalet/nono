# Generator recovery verification

- FarsiBlog scheduled run 38566744748 published posts 26, 27 and 28; all three public pages returned HTTP200 with article/image/FAQ content verified. This preceded the new recovery changes.
- RoyaBlog and RozBlog latest public pages returned HTTP200. Existing Roya cadence was not changed.
- FarsiBlog/RozBlog cadence updated to four checks/hour with shared manual/scheduled rolling budget of three verified publications per blog per 60 minutes.
- Controlled FarsiBlog run 38567344413 read the recovery commit, but correctly skipped generation and publication because the publication budget was full. It does NOT prove full repaired hose generation/publication.
- Read-only diagnostic 38568572464 passed source-page hose image review (score80), without generating text, attempting publication or modifying the queue. Exact returned review is stored separately, bound to pixel SHA256, family and policy.
- 111 local automation tests passed. New scheduler workflows discover all test_*.py files.
- Full repaired hose generation/publication remains to be verified on a subsequent quota-eligible execution. Native intermittent protected-panel HTTP403 is not claimed permanently resolved.
