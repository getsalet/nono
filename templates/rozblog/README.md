# AFP RozBlog template

The live template is `afp-main.html`. Native settings are part of pagination:

- Homepage post count (`ipnum`): **6**.
- Internal page post count (`opnum`): **6**.
- Ordering (`order_by`): **newest first**, value `1`.
- Homepage “Show more” (`show_more_home`): **off**. Use the native `Blog_Page_Block` pager instead of AJAX appending.

Use the original `ROZBLOG` post loop and native pagination. Do not fetch the homepage on every numbered page, or hide excess posts with a six-element JavaScript slice: that loses access to the remaining posts. `/pages/N` uses the same excerpt-card transform as the homepage; single permalinks retain the full article. The marketing header stays homepage-only. Numbered pages have their own canonical URL.

Verified 2026-10-14: home 6, `/pages/2` 6, `/pages/3` 3, 15 unique post URLs across those pages. Desktop 1440px and mobile 390px checked; single post retained its image and three FAQ blocks. Counts on the last page change as publication continues.
