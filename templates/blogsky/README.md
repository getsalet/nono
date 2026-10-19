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
- No generator workflow, schedule, article publication, or credentials were changed or enabled.

## Editing constraints

The current Blogsky panel exposes colors/header/widgets, but no global HTML/CSS theme editor. Thus the dedicated homepage's CSS does not alter ordinary posts. The single-post wrapper must accompany each new post. Do not claim it is globally installed or integrated into the generator until an actual publisher uses it.

## Source

https://navar-abyari.ir/ — footer/contact and category links checked 2026-10-19.

## Rollback

Set the start page back to “نمایش آخرین نوشته‌ها” in General settings. For a post using this wrapper, remove the `afp-post-skin` style and unwrap `#afp-post` while preserving article HTML.
