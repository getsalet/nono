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

## Readiness boundary
These secret names are the agreed connection contract. No Parsiblog publishing workflow/adapter is implemented by this theme change. Creating the secrets does not activate publishing. A later integration must verify login and editing, prevent duplicate posts, test a draft, and validate public content before claiming generator readiness. No articles were published in these theme tests.
The provider's current admin/blog URLs use HTTP. Do not assume HTTPS transport or describe this login as encrypted.
