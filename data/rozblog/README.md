# AFP city-image backlink pipelines

FarsiBlog: afp.farsiblog.com. RozBlog: afp-pipe.rozblog.com (not spadan1 or drip-irrigation).

Only target metadata is shared; each blog has a separate angle, AI call, artifact, queue and checkpoint. Matrix titles are authored separately for each blog and are not claimed to be the exact prior matrix. data/blog-city-title-matrix.json now contains newly authored independent city and article title matrices, approved under the user request to construct these matrices. This gate prevents new AI calls and publication, preserving all legacy records.

After approval, each queue is built from verified city/product targets in data/roya/backlink-queue.json; province hubs are not emitted as city articles. Exactly one actual image from the city destination is reused, with measured dimensions and descriptive alt. No invented local scene or missing-image fallback.

500–1000 Persian words, assigned matrix title, three FAQs and contextual city/province plus one homepage link (tape) or product shop reference (hose). No forced tape keyword in hose articles, numerical prices, local claims, keyword stuffing or replicated paragraphs. Originality checks cover Roya, FarsiBlog and RozBlog; incomplete history fails closed.

Maximum three verified posts per rolling 60 minutes per blog, shared by manual and scheduled runs. Native protected forms only, active-blog verification, title scan, per-post checkpoints and public article/image/link verification. No blind retry after uncertain submit.

RozBlog schedule: hourly at minute 35 only when repository variable ROZBLOG_AUTOMATION_ENABLED=1. Required repository secrets: AGNES_API_KEY and ROZBLOG_USERNAME, ROZBLOG_PASSWORD. Interactive email OTP cannot authenticate unattended GitHub runners. Nothing secret or private template backup belongs in this public repository.

Status: newly authored matrices configured; RozBlog unattended credentials and live-publication test are still required. Public access from the current computer returned HTTP403/timeouts, so public verification must be tested from the real runner before enabling schedules.

Product-family image gate: every candidate image is inspected against the corresponding approved AFP reference with a mandatory vision response and score >=70. A wrong, mixed, unknown, invisible or unreviewed product is rejected. Cache binds policy + expected family + SHA-256 of actual pixels. Image bytes are fetched/reviewed again before publication; a changed URL/hash cannot reuse old approval. This adapts reference-family routing from kikibox/maghala2 and strict visual checks from getsalet/nono; it does not enable their permissive fast-mode bypasses.
