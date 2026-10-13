# AFP فارسی‌بلاگ

وبلاگ: https://afp.farsiblog.com — قالب در پنل وبلاگ نگهداری می‌شود؛ پشتیبان خصوصی قالب وارد مخزن عمومی نمی‌شود.

- صف و سابقه مستقل؛ مقاله‌های آموزشی با زاویه جدا از مطالب خرید شهری رویا.
- متن ۵۰۰–۱۰۰۰ کلمه فارسی، سه FAQ بومی، دو ارجاع متنی مرتبط؛ حداکثر یک لینک صفحه نخست و بدون تکرار مقصد. عکس واقعی مرتبط از سایت، نه تصویر ساختگی محصول.
- تشابه واژگانی و پاراگراف‌های بلند با خروجی‌های تأییدشده هر دو وبلاگ بررسی می‌شود. این کنترل تضمین معنایی یا رتبه گوگل نیست.
- تصویر متفاوت جای متن اختصاصی را نمی‌گیرد. صفحه نخست باید مرجع مرتبط باشد، نه هدف تکرار افراطی کلیدواژه.
- ادعاهای عددی/محلی/تجاری نامستند، لینک‌های اشتباه و خروجی‌های بدون QA منتشر نمی‌شوند. نبود کلید AI هرگز نمونه ساختگی قابل انتشار تولید نمی‌کند.

## راه‌اندازی
Secrets مخزن: `FARSIBLOG_USERNAME`, `FARSIBLOG_PASSWORD` و کلید Agnes موجود. هیچ رمز در فایل‌های مخزن ذخیره نشود.
Workflow: **FarsiBlog original content pipeline**. برای نخستین آزمون واقعی `count=1`, `publish=0`, `dry_run=0`. برای انتشار صف آماده `count=0`, `publish=1`.
پس از تأیید نخستین انتشار، متغیر مخزن `FARSIBLOG_AUTOMATION_ENABLED=1` زمان‌بندی ساعتی را فعال می‌کند (دقیقه ۱۵ هر ساعت، حداکثر ۳ مقاله در هر اجرا). تا آن زمان اجرای زمان‌بندی عمداً غیرفعال است.
حداکثر سه مقاله در هر اجرای ساعتی؛ تا تخلیه صف آماده، مقاله تازه تولید نمی‌شود. هر انتشار از فرم بومی ثبت و سپس عنوان، لینک‌ها و FAQ در سایت زنده تأیید می‌شود. عنوان موجود در پنل برای جلوگیری از ارسال دوباره بررسی می‌شود.
صف برنامه‌ریزی‌شده محدود است؛ موضوع تازه فقط با زاویه مفید و غیرتکراری اضافه شود. پس از پایان صف، محتوای خودکار بی‌هدف تولید نمی‌شود.

افزایش تعداد پست، جایگزین کیفیت نیست: فقط مقالات تأییدشده و غیرتکراری منتشر می‌شوند. با پایان موضوعات صف، انتشار تازه متوقف می‌شود تا موضوعات مفید جدید اضافه شوند.

سقف ۳ انتشار تأییدشده در هر بازه متحرک ۶۰ دقیقه، علاوه بر سقف هر اجرا اعمال می‌شود. اجرای دستی و زمان‌بندی‌شده سهمیه مشترک دارند. اگر سهمیه پر باشد، تولید تازه و انتشار متوقف می‌شود و پیش‌نویس‌های تأییدشده در صف می‌مانند؛ پس از آزادشدن سهمیه، اجرای بعدی ادامه می‌دهد.


## City-image upgrade
# AFP city-image backlink pipelines

FarsiBlog: afp.farsiblog.com. RozBlog: afp-pipe.rozblog.com (not spadan1 or drip-irrigation).

Only target metadata is shared; each blog has a separate angle, AI call, artifact, queue and checkpoint. Matrix titles are authored separately for each blog and are not claimed to be the exact prior matrix. data/blog-city-title-matrix.json now contains newly authored independent city and article title matrices, approved under the user request to construct these matrices. This gate prevents new AI calls and publication, preserving all legacy records.

After approval, each queue is built from verified city/product targets in data/roya/backlink-queue.json; province hubs are not emitted as city articles. Exactly one actual image from the city destination is reused, with measured dimensions and descriptive alt. No invented local scene or missing-image fallback.

500–1000 Persian words, assigned matrix title, three FAQs and contextual city/province plus one homepage link (tape) or product shop reference (hose). No forced tape keyword in hose articles, numerical prices, local claims, keyword stuffing or replicated paragraphs. Originality checks cover Roya, FarsiBlog and RozBlog; incomplete history fails closed.

Maximum three verified posts per rolling 60 minutes per blog, shared by manual and scheduled runs. Native protected forms only, active-blog verification, title scan, per-post checkpoints and public article/image/link verification. No blind retry after uncertain submit.

RozBlog schedule: hourly at minute 35 only when repository variable ROZBLOG_AUTOMATION_ENABLED=1. Required repository secrets: AGNES_API_KEY and ROZBLOG_USERNAME, ROZBLOG_PASSWORD. Interactive email OTP cannot authenticate unattended GitHub runners. Nothing secret or private template backup belongs in this public repository.

Status: newly authored matrices configured; RozBlog unattended credentials and live-publication test are still required. Public access from the current computer returned HTTP403/timeouts, so public verification must be tested from the real runner before enabling schedules.
