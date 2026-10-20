# AFP Blogsky design

## Installed

- Blog: https://afp-pipe.blogsky.com/
- Dedicated home page: `/afp-home`, page ID `8352807900`; selected as the static start page in Blogsky General settings.
- `afp-home.html`: exact dedicated-home HTML/CSS source. Maximum desktop content width 1320px. Mobile layout unchanged except a fixed `tel:+989134922013` contact button and safe bottom spacing.
- Rich footer uses the official AFP site's product-category, warranty, after-sales, quality-test, returns, articles, contact, email and Bale links. Factory address and primary phone were checked against the official site's footer.
- Native Links app installed. Five links in the “دسته‌های محصولات AFP” group are enabled in the native sidebar. Native statistics remain server-rendered; no visitor counts are hardcoded in any template.

## Single-post template: prepared, not deployed to a published post

`afp-single-post.html` is an HTML body wrapper, NOT a global Blogsky theme and NOT a complete HTML document. Replace the single `{{ARTICLE_HTML}}` token with the QA-approved article body, then submit the resulting fragment through Blogsky's post HTML editor or a future publisher. Blogsky supplies the post title, metadata and live sidebar/statistics. Do not inject this wrapper into excerpts or the home page.

- The page-specific CSS is activated only when `#afp-post` exists.
- Desktop: 1320px overall width, 300px native sidebar, 32px gap; article text limited to 800px inside its column.
- Mobile/tablet: one column with the native sidebar below the article. Mobile click-to-call buttons are in-flow before and after article content/footer to avoid obscuring reading text.
- The rich article footer and product sidebar are based on the same official AFP URLs as the homepage.
- There are no Blogsky posts published yet. The single-post layout was rendered locally against a snapshot of the native Blogsky page and real server-rendered sidebar structure. It MUST be checked against the first actual published post before claiming end-to-end publication acceptance.
- Native statistic values in previews are snapshots, not a live analytics widget. The deliverable template does not contain those values.
- The generator connection below has now been added. No schedule, native article publication, or credential validation has been enabled/performed.

## Editing constraints

The current Blogsky panel exposes colors/header/widgets, but no global HTML/CSS theme editor. Thus the dedicated homepage's CSS does not alter ordinary posts. The single-post wrapper must accompany each new post. The export adapter now applies this wrapper after raw-article QA. This is not a globally installed theme or a verified native publishing integration.

## Source

https://navar-abyari.ir/ — footer/contact and category links checked 2026-10-19.

## Rollback

Set the start page back to “نمایش آخرین نوشته‌ها” in General settings. For a post using this wrapper, remove the `afp-post-skin` style and unwrap `#afp-post` while preserving article HTML.


## City generator connection (review/export only)

- Workflow: `.github/workflows/blogsky-content.yml`, **Blogsky city generator (review-only)**. Manual dispatch only; `dry_run=true` by default. No cron, push trigger, image-worker handoff or unattended native publisher.
- Adapter: `automation/blogsky_backlink_queue.py` loads a private instance of the existing `farsiblog_backlink_queue.py` engine. It does not duplicate the generator or retarget other blogs' globals/environment on import.
- Targets: exactly the existing city destinations in `data/roya/backlink-queue.json`; no province hubs, fabricated city URLs or general site-article targets. Only target metadata is shared, never article prose. Blogsky has its own titles, editorial angles, progress and drafts.
- Raw article QA is unchanged: 500–1000 Persian words, assigned city title, three FAQs, sections/checklist, semantic/claim checks and exactly two contextual backlinks (matching city + relevant home/shop destination). Footer/navigation links are not article backlinks and are outside `.afp-article-body`.
- Originality checks now include Blogsky checkpoints for all blogs. Missing approved history still fails closed; wrapped footer text must not enter the originality corpus.
- The existing explicit stop, per-family holds (including hose), rolling three-publications/60-minute budget and backlog cap remain effective. Blogsky is capped at **one newly approved draft per manual run** during setup. No holds or four-blog schedules/monitors were changed.
- Blogsky is explicitly added to the existing tape20 exact-source-image reuse scope. Keep the original linked-page image URL if available; do not generate new images. The source policy's text-only/required-illustration checks still apply. Blogsky is NOT added to the generated-image worker's enabled blogs.
- Configuration: `data/blogsky/generator-control.json` is deliberately `city_export_only` with `publication_enabled=false`; `BLOGSKY_PUBLISH=1` is rejected before queue changes. `BLOGSKY_USERNAME` / `BLOGSKY_PASSWORD` are not used, read or tested by this export-only adapter. Existing Agnes repository secrets are used only for an explicitly requested real generation run.

### Commands

```bash
# Read-only default: no API calls, queue writes, exports or native login
python automation/blogsky_backlink_queue.py

# Real content generation, one approved draft maximum; still NO publication
BLOGSKY_DRY_RUN=0 BLOGSKY_COUNT=1 python automation/blogsky_backlink_queue.py

# Revalidate/export existing completed drafts without new AI generation
BLOGSKY_DRY_RUN=0 BLOGSKY_COUNT=0 python automation/blogsky_backlink_queue.py
```

Optional `BLOGSKY_TARGET=city-<16 hex>` selects an exact existing queue key; an unknown or held-family target is rejected before provider calls. An existing ready backlog is exported/reused, not regenerated.

### Durable outputs and review

- Queue: `data/blogsky/backlink-queue.json` (created only on a real run).
- Draft/QA records: `artifacts/blogsky-backlink-queue/items/`.
- Generation progress: `state/blogsky-backlink-progress.json`; `generation-status.json` is generation-only, never evidence of publication.
- Review manifest: `artifacts/blogsky-backlink-queue/exports/index.json`. Only its current items are authorized for review. The manifest is invalidated before revalidation; old immutable HTML files are not readiness/publication evidence.
- Wrapped HTML fragments: the manifest's `body_file` values. Title, slug, tags and meta description are separate manifest fields; only supported native Blogsky fields should be filled during manual review. Do not claim Blogsky exposes an editable meta-description/slug field until inspected.
- The exporter reruns full raw-article QA instead of trusting a stored pass, then injects it into the single `{{ARTICLE_HTML}}` placeholder. It stores article/template/body hashes and never sets `published`, native IDs or public URLs.
- Actions uploads checkpoints even after a generation/export failure, then commits only Blogsky outputs and existing read-only originality caches. Conflicts fail closed and keep the recovery artifact.

**Acceptance boundary:** local tests and read-only production-queue preflight are not a successful Agnes generation, login or native Blogsky publication. Next release step is a deliberately approved first real draft and native-editor verification (including HTML sanitization, full article/FAQ/backlink persistence, sidebar/statistics, mobile/desktop layout and duplicate-safe reconciliation). Only then implement/enable the unattended native publisher; keep schedule off until that acceptance passes.


## Source-derived single-post footer

The single-post footer now includes AFP branding, product categories, warranty/after-sales/quality-test/inspection/request links, factory phone/email/Bale/address, site quick links and language navigation, derived from https://navar-abyari.ir/. It excludes inactive newsletter forms and unverified trust seals. Scoped CSS leaves the homepage and native sidebar unchanged; article prose, header and its two contextual backlinks remain outside the footer. This wrapper is used for future exports, not a global theme or an enabled publication schedule.


### Independent wide footer layout

Single-post CSS now promotes the footer into its own native page-grid row with `display: contents` on layout-only wrappers. Desktop footer spans both article and sidebar columns (1320px maximum); mobile footer follows the sidebar in the normal document flow. Article tags and author metadata remain above the separate footer. No JavaScript relocation, absolute footer, fixed height, homepage change or publication-schedule change is used.


### Edge-to-edge header and footer backgrounds

Header backgrounds span the viewport and the footer uses a horizontally extended, vertically clipped background shadow to reach both viewport edges without horizontal overflow. Footer corners are square. Inner content stays centered in the existing 1320px maximum page grid with responsive mobile gutters. The independent footer row and article content are unchanged.


## Current homepage: native live recent-post cards

`afp-home.html` promotes the native Recent Posts widget into the custom homepage grid. It displays up to six actual latest posts in three desktop columns and one narrow-screen column, preserving the existing hero, products and site footer. No inline script is required: Blogsky's page renderer strips scripts, so the earlier client-side-fetch prototype was discarded. The native latest-widget count, normal posts-per-page and `/posts` archive count are all set to six. Older posts are accessed through the native paginated archive; this is not an inline JavaScript pager on the static homepage.

No count/explanation sentence is shown above or below the cards. No fabricated or duplicate posts were published to fill six slots. Cover CSS for the latest actual posts is synchronized from each public article’s own verified source image by `automation/sync_blogsky_home_images.py` after successful native publication. The synchronizer patches only its marked CSS block in the existing homepage; article content, counts, scheduling and page settings are unchanged. The source is the native server widget, so newly published titles appear without resaving this homepage.

`data/blogsky/home-display.json` records the intended panel settings and implementation boundary. `data/blogsky/title-matrix.json` is the separate reproducible generator-title review export; it does not enable article generation or publication.
