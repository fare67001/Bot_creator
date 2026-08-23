# Bot Factory Pro

کارخانه ساخت ۱۰۰ قالب ربات تلگرام (aiogram 3 + PostgreSQL).

## UI
فقط دکمه‌های **Inline داخل چت** — بدون کیبورد پایین صفحه.

## اجرا
```bash
pip install -r requirements.txt
export BOT_TOKEN=...
python bot.py
```

## خروجی هر قالب
ZIP شامل `bot.py`، `requirements.txt`، `.env.example`، `README.md`  
نیاز به `DATABASE_URL` (PostgreSQL) روی Railway.

## دسته‌ها
فروش، خدمات، رزرو، آموزش، رویداد، جامعه، املاک، مالی، ابزار، انتشار — جمعاً ۱۰۰ قالب.


## Mini App
1. سرویس جدا برای مینی‌اپ: `python webapp_server.py`
2. روی سرویس **ربات** متغیر `WEBAPP_URL=https://DOMAIN` (حتماً https)
3. دکمه «استودیو مینی‌اپ» + دکمه منوی تلگرام
4. با `sendData` از مینی‌اپ، ZIP ساخته می‌شود
