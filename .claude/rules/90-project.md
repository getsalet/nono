# Project profile: nono

Purpose: generate, review, package, and upload Persian city landing posts.

Invariants:
- City jobs use exactly three final article images unless a versioned migration changes the contract and tests.
- Failed image QA must be quarantined/deferred so it cannot starve the queue.
- Completed posts and approved images are preserved during retries and rebuilds.
- Every 50 completed posts form a versioned package with manifest, SQL, rollback, item JSON, and images.
- FTPS upload selects only files named by the new-batch signal; never bulk re-upload all packages.
- Retry exhausted/pending records only after fixing the root cause and recording the retry policy version.
- City watchdog and worker must not share a cancel-prone concurrency group.

Relevant tests: `tests/test_city_image_policy.py`, `tests/test_new_batch_upload.py`.
