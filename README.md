# 🤖 Bot Factory Pro v8

## 100 قالب + دکمه‌های رنگی + آموزش استقرار

این نسخه برای Deploy روی Railway آماده شده و وابستگی‌ها روی `aiogram==3.30.0` و `python-dotenv==1.0.1` قفل شده‌اند.

### GitHub
این فایل‌ها را در ریشه Repository قرار بده:
- `bot.py`
- `templates.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`

توکن واقعی یا `.env` را روی GitHub قرار نده.

### Railway
1. Repository را به Railway وصل کن.
2. Variable زیر را در Service → Variables قرار بده:
```env
BOT_TOKEN=توکن_ربات_ساز
```
3. Start Command:
```bash
python bot.py
```
4. Deploy و Logs را بررسی کن.

`ADMIN_ID` برای خود Bot Factory لازم نیست؛ ربات‌های تولیدشده ممکن است آن را لازم داشته باشند.

### تست نسخه
- `py_compile` ربات‌ساز و موتور قالب‌ها
- تولید و compile هر 100 قالب
- بررسی 10 دسته × 10 قالب
- بررسی یکتایی کلیدها
- بررسی مسیر generator برای همه kindها
- پاک بودن بسته از `__pycache__`

تست اتصال واقعی به Telegram API در محیط آفلاین انجام نشده و باید بعد از Deploy با توکن واقعی انجام شود.
