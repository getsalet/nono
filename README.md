# Navar Abyari city-content automation

Automation for generating, reviewing, packaging, and uploading Persian city landing posts for `navar-abyari.ir`.

## Production flow

1. GitHub Actions selects one pending city/topic queue item.
2. Agnes generates and reviews the Persian article and five WebP images.
3. Quality gates validate language, grounding, links, FAQ structure, topic focus, and image markers.
4. Idempotent WordPress SQL and marker-protected rollback SQL are generated.
5. Every 50 completed posts are packaged into a ZIP containing SQL, item JSON, images, and a manifest.
6. New or changed packages are uploaded once through the separate FTPS workflow.

## Required secrets and variables

- `AGNES_API_KEY`
- `FTP_PASSWORD`
- `WORDPRESS_DB_NAME` defaults to `navaraby_wp569`
- WordPress table prefix is currently `ha_`

## Safety guarantees

- SQL begins with `SET NAMES utf8mb4` and an explicit `USE` statement.
- Re-importing generated SQL does not duplicate posts or attachments.
- Rollback deletes only posts carrying the queue's generation marker.
- Failed items remain visible and require an explicit repair retry.
- Interrupted `processing` items are recovered on the next run.
- Existing uploaded ZIPs are preserved; incomplete, corrupt, or not-yet-uploaded legacy packages are repaired.

## Manual repair run

Run the city-content workflow with `RETRY_FAILED=1` only after the underlying prompt, model, or code problem has been fixed.
