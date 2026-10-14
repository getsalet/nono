# Roya native card fallback

The live agent browser initially showed 290–330 character excerpts and no JavaScript errors. The user's report of full articles was not reproduced in that browser, so no browser-cache cause is claimed as proven.

The earlier layout nevertheless depended on JavaScript to remove full article content from the visible listing. The native template now emits a listing-only inline stylesheet inside fb:blog_page, before the post loop. This keeps a two-column desktop / one-column mobile card grid and bounds the visible excerpt to four lines (120px), even with JavaScript disabled. The original full article HTML remains in the listing response but is visually clipped; it is not falsely described as a server-generated text-only summary.

The listing includes native page links and unconditional read-full-article links without JavaScript. With JavaScript enabled, product image previews and short text extraction still work, and pagination appears above and below the cards.

Live tests at widths1366 and390, with JavaScript both on and off: six cards, visible text area90–120px, no horizontal overflow, article links available. Native page2 was checked in both modes. A full article retained the same673 whitespace-separated text words and height2174px in both modes, with no listing-fallback stylesheet emitted.

Native template save was read back exactly. Stored comments and article content were not changed.
