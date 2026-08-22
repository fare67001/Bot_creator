# Bot Factory Pro v11 — 100 Commercial Templates

کارخانه ساخت ربات‌های Telegram با 100 قالب تخصصی.

## اجرای خود Bot Factory

```bash
pip install -r requirements.txt
python bot.py
```

Variable اجباری:

```text
BOT_TOKEN=توکن ربات‌ساز
```

## خروجی هر قالب

وقتی کاربر یک ربات می‌سازد، یک بسته ZIP مستقل دریافت می‌کند:

- `bot.py`
- `requirements.txt`
- `.env.example`
- `README.md`

هر ربات خروجی PostgreSQL دارد و برای Railway آماده شده است.

## دیتابیس ربات‌های خروجی

هر ربات خروجی باید یک PostgreSQL جداگانه یا یک دیتابیس/Schema مجزا داشته باشد. در Railway می‌توان یک PostgreSQL Service به پروژه اضافه کرد و `DATABASE_URL` را به سرویس ربات متصل کرد. Railway برای PostgreSQL متغیرهایی مانند `DATABASE_URL` را در اختیار سرویس‌های پروژه قرار می‌دهد.

داده‌هایی که ربات از Telegram دریافت می‌کند در PostgreSQL ذخیره می‌شوند؛ از جمله پروفایل قابل‌دسترسی کاربر، پیام‌ها و رسانه‌های دریافتی، callbackها و داده‌های تخصصی قالب.

شماره تلفن فقط زمانی قابل ذخیره است که کاربر خودش Contact را برای ربات ارسال کند؛ ربات به شماره تلفن خصوصی کاربر بدون ارسال آن دسترسی ندارد.

## دریافت دیتابیس

در پنل مدیریت هر ربات گزینه:

**💾 دریافت دیتابیس**

یک Logical Backup فشرده با فرمت `.sql.gz` می‌سازد و برای ادمین ارسال می‌کند. برای دیتابیس‌های بزرگ‌تر از محدودیت ارسال Telegram، از Backup/`pg_dump` خود PostgreSQL استفاده کنید.

## Railway برای هر ربات خروجی

1. ZIP را Extract کن.
2. فایل‌ها را مستقیم در ریشه GitHub Repository قرار بده.
3. Railway → New Project → Deploy from GitHub Repo.
4. یک PostgreSQL Service به همان Project اضافه کن.
5. Variables ربات:
   - `BOT_TOKEN`
   - `ADMIN_ID`
   - `DATABASE_URL`
   - `CHANNEL` فقط برای قالب‌های کانالی
   - `PAYMENT_URL` فقط در صورت استفاده
6. Start Command:

```bash
python bot.py
```

7. Deploy و Logs را بررسی کن.
8. Telegram → `/start`.

## امنیت

`BOT_TOKEN` و `DATABASE_URL` را در GitHub Commit نکن. فقط در Railway Variables قرار بده.

## نکته فنی

Telegram فقط داده‌هایی را در اختیار Bot قرار می‌دهد که در Updateهای Bot API موجود باشند؛ «تمام اطلاعات کاربر» به معنی تمام اطلاعات قابل‌دسترسی برای Bot است، نه اطلاعات خصوصی خارج از Telegram Bot API.
