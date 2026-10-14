# AFP FarsiBlog card template

Verified live template for https://afp.farsiblog.com/.

Native panel settings: `lhpost = 6` and `lopost = 6` under User/NormalSetting. These settings provide real server-side pagination; the template does not fabricate page links.

Listing pages display a responsive two-column card grid on desktop and one column on mobile. Cards retain the approved post image, title, metadata, short visible excerpt and full-post link. Existing post content and URLs are unchanged; full content and three article FAQs remain on single-post routes. Light and dark modes inherit the original theme.

FarsiBlog strips backslashes during template saves. New card code therefore uses `new RegExp` and character classes without literal backslashes. Always reload the native editor after saving and compare the complete source. Do not paste compiled public HTML as a template.

Provider-injected advertising is not removed by this template. Advertising was excluded only from offline layout previews used for visual QA.
