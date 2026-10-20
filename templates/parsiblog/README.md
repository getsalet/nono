# AFP Parsiblog theme and generator connection contract

Live blog: http://afp.parsiblog.com/

## Theme
- `afp-main.html` is the editable native Parsiblog template installed on the live blog.
- `backup-before-responsive-v2.html` is the template before this responsive revision.
- `verification-v2.json` records live browser checks, not a publishing acceptance test.
- Fluid desktop layout, native details/summary mobile menu, consistent responsive borders.
- Targeted CSS hides the provider's current injected ad widget, identified by its own close/open image URLs; numeric IDs are not hardcoded. Provider changes can require updating this rule. This is display suppression, not account-level ad removal or blocking the ad network request.
- Parsiblog normalizes Persian letters/entities when saving; the saved editor text can differ from source.

## Repository Actions secrets for the future Parsiblog adapter
Create only these new repository secrets under Settings > Secrets and variables > Actions:

| Name | Value |
| --- | --- |
| PARSIBLOG_USERNAME | The user's Parsiblog login username |
| PARSIBLOG_PASSWORD | The user's Parsiblog login password |

Never commit these values or include them in logs or issue comments.
The public URL is not a secret. Reuse existing generation-provider secrets when wiring this provider into the existing generator.

## Rich footer and generator integration
The installed footer uses real main-site article, product, service, contact, email, Bale and map links. Styles are loaded from a pinned immutable CSS commit because the provider enforces a 40,960-character editor limit. The mobile menu remains native details/summary.

Generator code and the 1,000-title evidence-safe inventory are in automation/parsiblog_*.py and data/parsiblog/. See data/parsiblog/README.md for exact three-link rules and readiness boundaries. Secret-backed login/draft/publication are separate checks; code installation alone is not successful activation. The hourly schedule remains disabled until an actual public canary is verified.
