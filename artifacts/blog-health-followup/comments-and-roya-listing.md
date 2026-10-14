# Comments removal and Roya listing verification

## Comments
- Removed comment forms, per-post comment links and comment-list output from the native RoyaBlog, FarsiBlog and RozBlog templates. Roya latest-comments sidebar was removed too.
- Native CommentSetting pcomment was saved unchecked and read back on RoyaBlog and FarsiBlog.
- Disabled native RozBlog pcm for all 18 existing posts, with per-post readback. Native title/body/tags/status/member fields were checked unchanged; multipart CRLF normalization was accounted for before permitting the save. No stored comments were deleted.
- Shared Roya/Farsi publisher now explicitly unchecks pcomment; Roz publisher uses pcm=2 for future posts. Commit: 7d6e004fbab255512793a4193c482a20b1091d84.
- Homepages and an article on each blog returned HTTP200 with no comment form or per-post comment link.

## Roya article index
- Native settings already had lhpost=6 and lopost=6. Native page links and post loop were retained, not replaced by client-side pagination.
- Converted the article listing to two columns on desktop and one on mobile. Long home introduction is hidden only in listing mode; category navigation and sales banner are retained after the index.
- Native page selection appears above and below cards, with active-page state and previous/next links copied only from actual server-provided links.
- Live home, page2 and page3 each showed six distinct posts, six previews, two pagers and no horizontal overflow. No overlap between those three page sets was found during verification.
- Mobile width390 and desktop width1366 were checked. Product images kept their natural aspect ratio. No JavaScript page errors were observed.
- The checked full article (post109) retained its full body (536 whitespace-separated words including collapsed FAQ answers), with zero card excerpts and zero comment forms.
- Native Roya template saving strips backslashes; the listing script avoids them and the saved source was read back exactly.
- 119 repository unit tests passed locally after the final changes.
