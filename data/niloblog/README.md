# اتصال داده‌ای و ماتریس نیلوبلاگ AFP

مخزن: `getsalet/nono`، شاخه `main`؛ وبلاگ: https://afp.niloblog.com/

## فایل‌ها
- `title-index.md`: نسخه قابل مرور ۱۰۰۰ عنوان و مقاله مرتبط هر کدام.
- `title-matrix.json`: داده ساختاریافته؛ ۱۰۰۰ ردیف با شناسه پایدار، محل و محصول، زاویه مستقل و طرح لینک.
- `article-targets.json`: فهرست مقصدها؛ مقاله‌های مرتبط، منابع فنی کمکی و دو مقصد کلیدواژه.
- `destination-review.json`: نتیجه HTTP، URL نهایی، canonical، robots و اثرانگشت متن مقصدها. این بررسی، تأیید علمی محتوای مقاله یا تضمین ایندکس/رتبه نیست.
- `integration-plan.json`: قرارداد اتصال به مخزن و نام سکرت‌ها، بدون مقدار محرمانه.
- `automation/validate_niloblog_matrix.py` در ریشه مخزن: اعتبارسنج ساختاری fail-closed.

## نیازمندی‌های کاربر
۱. لحن مقاله‌ای، آموزشی و مسئله‌محور؛ نه متن تبلیغاتی انباشته از کلمه کلیدی.
۲. نام شهر/شهرستان + فقط یک کشت ردیفی + زاویه مشخص درباره آبیاری قطره‌ای یا نوار تیپ.
۳. دو تا سه لینک داخل متن: یک مقاله مرتبط + یک لینک طبیعی کلیدواژه؛ لینک سوم اختیاری و فقط با ارزش واقعی برای خواننده.
۴. دو عبارت کلیدی هدف «نوار تیپ» و «نوار آبیاری» هستند. هر دو نباید صرفاً برای تکمیل سهمیه به جمله تحمیل شوند.
۵. تصویر منتظر URL کاربر است؛ تولید یا انتخاب تصویر خودکار خاموش است.

## محدوده شواهد و کیفیت
این نسخه از ۸ ترکیب شهرستان–کشت دارای سابقه بررسی در `data/blog-city-crop-evidence.json` استفاده می‌کند؛ ۱۲۴ زاویه نگارشی برای هر ترکیب، ۹۹۲ پیشنهاد می‌سازد. ۸ نمونه پیشنهادی درچه–پیاز نیز با وضعیت نیازمند منبع محلی اضافه شده است. جمع دقیقاً ۱۰۰۰ عنوان، در ۹ مکان و ۴ کشت است. این عدد به معنای ۱۰۰۰ مکان، یا ۱۰۰۰ موضوع علمی مستقل و آماده انتشار نیست.

شهرستان طارم/بهار: سیب‌زمینی؛ شهرستان اسدآباد/تاکستان/ارومیه/میاندوآب: گوجه‌فرنگی؛ شهرستان آذرشهر/هوراند: سیر. نمونه درچه–پیاز تنها پیشنهاد کاربر است، نه شاهد کشت.

همه ردیف‌ها در مرحله بررسی نگارشی/محلی هستند. حتی ردیف‌های دارای سابقه منبع، برای فصل جاری، طراحی شبکه، کیفیت آب و ادعاهای فنی مجوز خودکار ندارند. تکرار یک زاویه در شهر دیگر به‌تنهایی محتوای جدید نیست؛ داده محلی مستقل و بررسی شباهت معنایی بین وبلاگ‌ها الزامی است. در نبود منبع، ردیف متوقف بماند؛ ادعای اقلیم، رواج کشت، زمان‌بندی آبیاری، فشار/آبدهی ثابت یا تضمین صرفه‌جویی ساخته نشود.

## اتصال و وضعیت اجرا
- نام سکرت‌ها: `NILOBLOG_USERNAME` و `NILOBLOG_PASSWORD`.
- فقط نام‌ها ثبت شده‌اند؛ مقادیر خوانده/ذخیره یا صحت آن‌ها تأیید نشده است.
- این مرحله اتصال داده‌ها به مخزن است. آداپتر ورود/پیش‌نویس/انتشار نیلوبلاگ و workflow عملیاتی هنوز ساخته نشده‌اند.
- `publication_enabled=false` و `workflow_enabled=false`. هیچ پست یا تصویری تولید/منتشر نشده است.
- فایل‌های کنترل جنراتورهای فعلی، توقف سراسری، خانواده hose و Blogfa بازنشسته تغییر نکرده‌اند.
- فعال‌سازی آینده منوط به مجوز انتشار، دریافت URL تصویر، آزمون بومی ذخیره و رسید عمومی، کنترل بودجه و توقف سراسری و بررسی محتوایی است.

## آزمون
```bash
python automation/validate_niloblog_matrix.py
python -m unittest discover -s tests -p 'test_niloblog_title_matrix.py'
```
اعتبارسنج به مدرک مشترک شهر–کشت نیاز دارد و در نبود آن fail-closed عمل می‌کند. تغییر وضعیت برای دور زدن بررسی مجاز نیست.

## اصلاح طول عنوان و مقاله
عنوان‌ها با حفظ شناسه، شهر/شهرستان، کشت، منبع و وضعیت بررسی کوتاه شدند. سقف نگارشی عنوان ۷۸ نویسه و هدف ۵۰ تا ۷۰ است؛ محدودیت قطعی گوگل محسوب نمی‌شود. هدف متن ۶۰۰ تا ۹۰۰ کلمه است؛ متن بیش از ۱۱۰۰ کلمه باید بازبینی شود. متن کوتاه و کامل بر متن کش‌دار اولویت دارد؛ تعداد کلمه عامل رتبه‌بندی یا تضمین سئو نیست. این پروفایل فقط برنامه نگارشی نیلوبلاگ است؛ نویسنده/ناشر عملیاتی هنوز پیاده نشده و انتشار و تصویر خودکار خاموش باقی می‌مانند.


## رسانه‌های آماده؛ انتشار همچنان خاموش
- `media-catalog.json`: ۳۷ تصویر WebP و ۹ ویدیو MP4 در پوشه عمومی معرفی‌شده توسط مالک.
- `media-links.md`: فهرست لینک‌ها؛ `media-conversion-report.json`: حجم و گزارش تبدیل.
- WebP با quality=65 از 100، با اعمال جهت EXIF، حذف متادیتا و حداکثر ضلع 1600 ساخته شد. این عدد کیفیت است، نه تضمین 65٪ کاهش حجم.
- نسخه‌های JPG اصلی حذف نشدند تا لینک‌های موجود نشکنند. تنها تصاویر جدید جنراتور به WebP ارجاع می‌دهند؛ هیچ مقاله قدیمی یا کتابخانه وردپرس بازنویسی نشده است.
- تصاویر: دانلود عمومی، MIME، decode کامل و SHA256 عین فایل آپلودشده تأیید شد. ویدیوها: هدر و فرمت/کدک/ابعاد/مدت با ffprobe بررسی شد، نه مشاهده کامل تمام فیلم‌ها.
- تصویر محصول/تولید/انبار، تصویر محلی مزرعه نیست؛ alt واقعی انتخاب شود، نه نام شهر و کشت جعلی.
- انتخاب تصویر نوبتی؛ ویدیو در احتمال پیشنهادی و قابل‌تنظیم 25٪، ثابت برای هر شناسه مطلب در تلاش مجدد. پخش خودکار ممنوع، controls و preload=none و اندازه منعطف. لینک قابل‌کلیک احتمالی ویدیو باید در سقف 2 تا 3 لینک بدنه حساب شود.
- `automation/niloblog_media.py` فقط helper بدون انتشار است. رزرو مجدد همان پست ثابت می‌ماند؛ تا تأیید مستقل رسید عمومی، نوبت تصویر جلو نمی‌رود. وضعیت مبهم باید reconcile شود. caller آینده مسئول قفل تک‌نویسنده، ذخیره اتمیک پایدار و بررسی واقعی رسید است.
- این helper هنوز به نویسنده بومی نیلوبلاگ متصل نشده است. حفظ HTML تصویر/ویدیو، پخش روی موبایل، مدیریت وضعیت، ورود با سکرت‌ها و انتشار نیازمند آزمون مستقل است. `publication_enabled`، `workflow_enabled` و `runtime_integration_enabled` همگی false می‌مانند.


## Runtime status — native provider blocker

- GitHub workflow: `.github/workflows/niloblog-content.yml`, scheduled at minutes 17 and 47 UTC; one candidate publication per cycle, hard ceiling two verified receipts per rolling hour.
- `NILOBLOG_USERNAME` / `NILOBLOG_PASSWORD` were present and an actual GitHub-runner sign-in succeeded. No credential values are stored in artifacts.
- Runtime revision 6 is **intentionally disabled**, phase `native_server_blocked`; the schedule's preflight exits before browser/API costs. User publication authorization remains recorded, but does not override a native failure.
- Native post ID 1 is private and held: CKEditor pretty-print linefeeds were corrupted into literal `nn` text. Corrected educational copy is stored in the item, but **was not saved or published natively**.
- Current new-post form rejects even a private save with `DB ERROR: Incorrect integer value: '' for column 'pcomment' at row 1`; the edit form returns an internal operation error. Supplying the existing moderation selector did not fix the provider error. No corrected private canary exists.
- The prepared adapter uses compact editor output, strict body/link/WebP/video round-trip checks, fresh source checks, factual/semantic originality review, durable write intents, and public permalink receipts. Its new-public-post path remains unverified and cannot run until the private canary gate is satisfied.
- No public post was submitted. No image cursor advanced. The original pending media selection remains reserved. No other blog's runtime or global controls were modified.
- Provider support must fix native new-post and edit errors. Then verify corrected private body, links, WebP decoding and selected video; run exactly one public canary; independently verify native permalink and media before enabling normal `publish` phase. Do not just toggle the runtime flag.
- See `artifacts/niloblog/native-server-blocker.json` for a non-secret native-state check. Never retry an ambiguous public submission automatically.
