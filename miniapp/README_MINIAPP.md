# Bot Factory Studio Mini App (1M design kit)

مینی‌اپ اختصاصی ربات‌ساز — جدا از ۱۰۰ ربات تولیدی.

## UI
- تم تیره نئون + تم روشن
- کاتالوگ، ویزارد، پیش‌نمایش برند، گالری، FAQ
- Haptic و Telegram WebApp

## Run
```bash
pip install -r requirements-webapp.txt
python webapp_server.py
```


## Audit notes
- `css/god-kit.css` (~1M lines) is archived in the package but **not linked** in `index.html` (would freeze Telegram WebView).
- Production styles use `god-kit-lite.css` + tokens/base/components/sections.
- XSS escape on dynamic HTML; path-traversal guard on static routes; admin id validation.
