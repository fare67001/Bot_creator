# Bot Factory FULL Bundle

این بسته دو بخش دارد:

## 1) `factory/` — ربات کارخانه (سازنده ۱۰۰ قالب)
- فایل‌ها: `bot.py`, `templates.py`, `requirements.txt`, `.env.example`
- Start Command (Railway): `python bot.py`
- Variables:
  - `BOT_TOKEN` = توکن ربات
  - `WEBAPP_URL` = آدرس https سرویس مینی‌اپ (مثال: https://xxx.up.railway.app)

## 2) `miniapp/` — استودیو مینی‌اپ
- Start Command: `python webapp_server.py`
- نیاز: `pip install -r requirements-webapp.txt`
- دامنه همین سرویس را در `WEBAPP_URL` ربات بگذار

## ترتیب پیشنهادی روی Railway
1. یک سرویس از پوشه `miniapp` بساز و دامنه بگیر
2. یک سرویس از پوشه `factory` بساز
3. در سرویس factory متغیر `WEBAPP_URL` را روی دامنه مینی‌اپ ست کن
4. Redeploy ربات

## نکته UI
- `miniapp/webapp/css/god-kit.css` (~1M خط) آرشیو طراحی است و در `index.html` لود نمی‌شود (وب‌ویو تلگرام قفل نشود).
- استایل واقعی: tokens + base + components + sections + god-kit-lite

## جریان کاربر
/start در ربات → دکمه «استودیو مینی‌اپ» → انتخاب قالب و برند → ارسال به ربات → دریافت ZIP
