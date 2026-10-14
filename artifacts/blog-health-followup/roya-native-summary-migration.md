# Roya native summary split: partial migration and provider blocker

## Root cause and code correction
The publisher previously wrote the entire article HTML into pshort and left pfull empty. CSS/JavaScript cards could hide the full body visually, but the server listing still received the entire article.

The Roya publisher now partitions the already-approved HTML after the first substantive introductory paragraph. pshort contains the original leading image and intro; pfull contains the continuation. Concatenating them reconstructs the original HTML exactly in the helper. This avoids duplicated text/images in Roya full pages, which concatenate these native fields. FarsiBlog shared-publisher behavior remains unchanged. Both native editors must be initialized before serialization.

## Actual live test
Post109 was split into693 characters of short HTML and3287 characters of continuation. The raw server homepage response contained only290 text characters for that article, not the full body. The existing article URL still returned HTTP200 with2824 text characters, one image and three FAQ blocks. The saved source reconstructed the original article modulo Roya's native Arabic/Persian yeh/kaf conversion.

## Important unresolved side effect
The native editing fallback changed post109's stored permalink to p_. The original long URL still returns the article, but the server-generated listing link now uses /post/109/p_. Restoration through the original Op edit route returned HTTP500. Common CMS permalink compatibility fields did not restore it. No bulk migration of the other existing posts was performed, to avoid changing their stored permalinks.

A separate legacy UI mismatch was found: its original submit handler reads #ptitleedit although the page renders #ptitle. Bridging that selector allowed the original Op request to run, but did not resolve its HTTP500.

The PostSetting noshort trial did not suppress the duplicated prefix on the tested split article; it was rolled back. The corrected before/after-Read-more partition does not rely on that option.

## Scope of completion
- Publisher code for future Roya articles is corrected and unit-tested.
- One existing article has a genuine server-rendered summary.
- Other existing articles have NOT been migrated to native summaries.
- Stored-permalink preservation on native existing-post edits remains a provider-side blocker. Full completion is not claimed.
