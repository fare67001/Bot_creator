# -*- coding: utf-8 -*-
"""Bot Factory Pro — سازنده ۳۰۰ قالب تخصصی (فقط دکمه‌های Inline داخل چت)."""
from __future__ import annotations

import asyncio
import html
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    BotCommand,
    BufferedInputFile,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    Message,
    WebAppInfo,
)
from dotenv import load_dotenv

import templates

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN تنظیم نشده است.")

WEBAPP_URL = (os.getenv("WEBAPP_URL") or os.getenv("MINIAPP_URL") or "").strip().rstrip("/")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bot_factory")
if WEBAPP_URL and not WEBAPP_URL.startswith(("http://", "https://")):
    log.warning("WEBAPP_URL ignored (need http/https): %s", WEBAPP_URL)
    WEBAPP_URL = ""
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
SEP = "━━━━━━━━━━━━━━━━"


class Build(StatesGroup):
    choosing = State()
    brand = State()
    welcome = State()
    admin = State()
    detail = State()


class Browse(StatesGroup):
    waiting_num = State()


PAGE_SIZE = 8


def ordered_templates() -> list[tuple[str, str]]:
    """لیست پایدار (کلید، عنوان) برای صفحه‌بندی و جستجو با شماره."""
    return list(templates.TEMPLATES.items())


def template_by_number(num: int) -> tuple[int, str, str] | None:
    items = ordered_templates()
    if num < 1 or num > len(items):
        return None
    key, label = items[num - 1]
    return num, key, label


def browse_page_kb(page: int) -> tuple[InlineKeyboardMarkup, int, int, int]:
    items = ordered_templates()
    total = len(items)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(0, min(int(page), pages - 1))
    start = page * PAGE_SIZE
    chunk = items[start : start + PAGE_SIZE]
    rows: list[list[InlineKeyboardButton]] = []
    for i, (key, label) in enumerate(chunk):
        num = start + i + 1
        title = (label or key)[:42]
        rows.append([
            InlineKeyboardButton(
                text=f"{num}. {title}",
                callback_data=f"bv:{num}",
                style="primary",
            )
        ])
    nav: list[InlineKeyboardButton] = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="◀️ قبلی", callback_data=f"bp:{page - 1}", style="primary"))
    nav.append(InlineKeyboardButton(text=f"{page + 1}/{pages}", callback_data="noop", style="primary"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton(text="بعدی ▶️", callback_data=f"bp:{page + 1}", style="primary"))
    rows.append(nav)
    rows.append([
        InlineKeyboardButton(text="🔎 جستجوی شماره ربات", callback_data="bs", style="success"),
        InlineKeyboardButton(text="🏠 خانه", callback_data="home", style="primary"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows), page, pages, total


def template_detail_kb(num: int) -> InlineKeyboardMarkup:
    total = len(ordered_templates())
    nxt = min(total, num + 1)
    prv = max(1, num - 1)
    rows = [
        [
            InlineKeyboardButton(text="🚀 ساخت این ربات", callback_data=f"bb:{num}", style="success"),
        ],
        [
            InlineKeyboardButton(text="⏭ بعدی", callback_data=f"bv:{nxt}", style="primary"),
            InlineKeyboardButton(text="⏮ قبلی", callback_data=f"bv:{prv}", style="primary"),
        ],
        [
            InlineKeyboardButton(text="📋 لیست قالب‌ها", callback_data="browse_all", style="primary"),
            InlineKeyboardButton(text="🏠 خانه", callback_data="home", style="primary"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def template_detail_text(num: int, key: str, label: str) -> str:
    meta = (getattr(templates, "TEMPLATE_META", {}) or {}).get(key) or {}
    engine = (getattr(templates, "ENGINE_BY_KEY", {}) or {}).get(key) or meta.get("engine") or "—"
    category = meta.get("category") or "—"
    features = meta.get("features") or []
    feat = " · ".join(str(x) for x in features[:8]) if features else "—"
    return (
        f"🤖 <b>ربات شماره {num}</b>\n"
        f"{SEP}\n"
        f"🏷 نام: <b>{html.escape(str(label))}</b>\n"
        f"🔑 کلید: <code>{html.escape(key)}</code>\n"
        f"📂 دسته: {html.escape(str(category))}\n"
        f"⚙️ موتور: <code>{html.escape(str(engine))}</code>\n"
        f"✨ امکانات: {html.escape(feat)}\n"
        f"{SEP}\n"
        "می‌تونی از همین‌جا بسازی، یا برگردی به لیست."
    )


def style_for(text: str, callback: str | None = None) -> str:
    t = (text or "").casefold()
    c = callback or ""
    if c.startswith("cancel") or any(x in t for x in ("لغو", "حذف", "رد", "خروج")):
        return "danger"
    if any(x in t for x in ("ساخت", "شروع", "تأیید", "ثبت", "افزودن", "دانلود", "ادامه")):
        return "success"
    return "primary"


def ikb(rows: list[tuple[str, str]], cols: int = 2) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, len(rows), cols):
        chunk = rows[i : i + cols]
        keyboard.append(
            [
                InlineKeyboardButton(text=t, callback_data=c, style=style_for(t, c))
                for t, c in chunk
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def home_text() -> str:
    return (
        "🤖 <b>BOT FACTORY PRO</b>\n"
        "<i>کارخانه ساخت ربات‌های تجاری تلگرام</i>\n"
        f"{SEP}\n"
        "🚀 <b>۱۰۰ قالب تخصصی</b> در ۱۰ دسته\n"
        "⚡ تولید کد آماده Railway + PostgreSQL\n"
        "🧩 هسته سفارش · رزرو · تیکت · امتیاز\n"
        f"{SEP}\n"
        "از دکمه‌های زیر شروع کن 👇"
        + ("\n✨ مینی‌اپ استودیو فعال است." if WEBAPP_URL else "\nℹ️ WEBAPP_URL را برای مینی‌اپ ست کن.")
    )


def home_kb() -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    if WEBAPP_URL:
        rows.append([
            InlineKeyboardButton(
                text="✨ استودیو مینی‌اپ",
                web_app=WebAppInfo(url=WEBAPP_URL),
                style="success",
            )
        ])
    base = [
        ("🚀 ساخت ربات جدید", "build_start"),
        ("✨ مشاهده ۳۰۰ قالب", "browse_all"),
        ("📊 آمار کارخانه", "stats"),
        ("🎓 آموزش راه‌اندازی", "guide"),
    ]
    for idx in range(0, len(base), 2):
        chunk = base[idx : idx + 2]
        rows.append([
            InlineKeyboardButton(text=t, callback_data=c, style=style_for(t, c))
            for t, c in chunk
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def cats_kb() -> InlineKeyboardMarkup:
    rows = [(label, f"cat:{label}") for label in templates.CATEGORIES]
    rows.append(("🏠 خانه", "home"))
    return ikb(rows, cols=1)


def templates_kb(category: str) -> InlineKeyboardMarkup:
    items = templates.CATEGORIES.get(category) or []
    rows = [(title, f"tpl:{key}") for key, title in items]
    rows.append(("↩️ دسته‌ها", "cats"))
    rows.append(("🏠 خانه", "home"))
    return ikb(rows, cols=1)


def cancel_kb() -> InlineKeyboardMarkup:
    return ikb([("🔴 لغو ساخت", "cancel_build"), ("🏠 خانه", "home")], cols=2)



@dp.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


@dp.callback_query(F.data == "browse_all")
async def cb_browse_all(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    kb, page, pages, total = browse_page_kb(0)
    await callback.message.edit_text(
        f"✨ <b>مشاهده همه قالب‌ها</b>\n"
        f"{SEP}\n"
        f"تعداد کل: <b>{total}</b> قالب\n"
        f"صفحه {page + 1} از {pages}\n"
        f"{SEP}\n"
        "یک مورد را انتخاب کن، یا با شماره جستجو کن:",
        reply_markup=kb,
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("bp:"))
async def cb_browse_page(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        page = int(callback.data.split(":")[1])
    except Exception:
        page = 0
    kb, page, pages, total = browse_page_kb(page)
    try:
        await callback.message.edit_text(
            f"✨ <b>مشاهده همه قالب‌ها</b>\n"
            f"{SEP}\n"
            f"تعداد کل: <b>{total}</b> قالب\n"
            f"صفحه {page + 1} از {pages}\n"
            f"{SEP}\n"
            "یک مورد را انتخاب کن:",
            reply_markup=kb,
        )
    except Exception:
        pass
    await callback.answer()


@dp.callback_query(F.data.startswith("bv:"))
async def cb_browse_view(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        num = int(callback.data.split(":")[1])
    except Exception:
        return await callback.answer("شماره نامعتبر", show_alert=True)
    found = template_by_number(num)
    if not found:
        return await callback.answer("ربات با این شماره پیدا نشد", show_alert=True)
    num, key, label = found
    try:
        await callback.message.edit_text(
            template_detail_text(num, key, label),
            reply_markup=template_detail_kb(num),
        )
    except Exception:
        await callback.message.answer(
            template_detail_text(num, key, label),
            reply_markup=template_detail_kb(num),
        )
    await callback.answer()


@dp.callback_query(F.data == "bs")
async def cb_browse_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Browse.waiting_num)
    total = len(ordered_templates())
    await callback.message.edit_text(
        f"🔎 <b>جستجوی ربات با شماره</b>\n"
        f"{SEP}\n"
        f"یک عدد بین <b>1</b> تا <b>{total}</b> بفرست.\n"
        f"مثال: <code>5</code> برای ربات شماره ۵",
        reply_markup=ikb([("📋 بازگشت به لیست", "browse_all"), ("🏠 خانه", "home")], cols=2),
    )
    await callback.answer()


@dp.message(Browse.waiting_num)
async def on_browse_num(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    if not raw.isdigit():
        return await message.answer(
            "فقط عدد بفرست — مثلاً 12",
            reply_markup=ikb([("📋 لیست", "browse_all"), ("🏠 خانه", "home")], cols=2),
        )
    num = int(raw)
    found = template_by_number(num)
    if not found:
        total = len(ordered_templates())
        return await message.answer(
            f"ربات شماره {num} وجود ندارد.\nبازه معتبر: 1 تا {total}",
            reply_markup=ikb([("📋 لیست", "browse_all"), ("🏠 خانه", "home")], cols=2),
        )
    await state.clear()
    num, key, label = found
    await message.answer(
        template_detail_text(num, key, label),
        reply_markup=template_detail_kb(num),
    )


@dp.callback_query(F.data.startswith("bb:"))
async def cb_browse_build(callback: CallbackQuery, state: FSMContext):
    """شروع ساخت از روی مشاهده شماره."""
    try:
        num = int(callback.data.split(":")[1])
    except Exception:
        return await callback.answer("نامعتبر", show_alert=True)
    found = template_by_number(num)
    if not found:
        return await callback.answer("پیدا نشد", show_alert=True)
    num, key, label = found
    if key not in templates.TEMPLATES:
        return await callback.answer("قالب نامعتبر", show_alert=True)
    await state.set_state(Build.brand)
    await state.update_data(template=key, template_label=label)
    await callback.message.edit_text(
        f"✅ قالب: <b>{html.escape(label)}</b>\n"
        f"شماره: <b>{num}</b>\n"
        f"{SEP}\n"
        "🏷 <b>نام برند / فروشگاه</b> را بفرست:\n"
        "مثال: <code>VIP Store</code>",
        reply_markup=cancel_kb(),
    )
    await callback.answer()



@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(home_text(), reply_markup=home_kb())


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 <b>راهنما</b>\n"
        f"{SEP}\n"
        "۱) ساخت ربات جدید را بزن\n"
        "۲) قالب را انتخاب کن\n"
        "۳) نام برند، خوش‌آمد و آیدی ادمین را وارد کن\n"
        "۴) جزئیات قالب (محصول/اسلات/…)\n"
        "۵) فایل ZIP آماده را دانلود و روی Railway اجرا کن\n",
        reply_markup=home_kb(),
    )


@dp.callback_query(F.data == "home")
async def cb_home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_text(home_text(), reply_markup=home_kb())
    except Exception:
        await callback.message.answer(home_text(), reply_markup=home_kb())
    await callback.answer()


@dp.callback_query(F.data == "guide")
async def cb_guide(callback: CallbackQuery):
    text = (
        "🎓 <b>آموزش راه‌اندازی خروجی</b>\n"
        f"{SEP}\n"
        "۱) از @BotFather توکن بگیر\n"
        "۲) ZIP را در GitHub بگذار\n"
        "۳) در Railway سرویس + PostgreSQL بساز\n"
        "۴) Variables:\n"
        "   • <code>BOT_TOKEN</code>\n"
        "   • <code>ADMIN_ID</code>\n"
        "   • <code>DATABASE_URL</code>\n"
        "۵) Start: <code>python bot.py</code>\n"
        "۶) Deploy و تست /start\n"
    )
    await callback.message.edit_text(text, reply_markup=home_kb())
    await callback.answer()


@dp.callback_query(F.data == "stats")
async def cb_stats(callback: CallbackQuery):
    n_cat = len(templates.CATEGORIES)
    n_tpl = sum(len(v) for v in templates.CATEGORIES.values())
    text = (
        "📊 <b>آمار کارخانه</b>\n"
        f"{SEP}\n"
        f"دسته‌ها: <b>{n_cat}</b>\n"
        f"قالب‌ها: <b>{n_tpl}</b> (۳۰۰)\n"
        "موتور: PostgreSQL + aiogram 3\n"
        "خروجی: bot.py + requirements + README\n"
    )
    await callback.message.edit_text(text, reply_markup=home_kb())
    await callback.answer()


@dp.callback_query(F.data == "cats")
async def cb_cats(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"✨ <b>۱۰ دسته قالب</b>\n{SEP}\nیک دسته را انتخاب کن (مسیر ساخت از دسته):",
        reply_markup=cats_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("cat:"))
async def cb_cat(callback: CallbackQuery):
    cat = callback.data[4:]
    if cat not in templates.CATEGORIES:
        return await callback.answer("دسته نامعتبر", show_alert=True)
    await callback.message.edit_text(
        f"📂 <b>{html.escape(cat)}</b>\n{SEP}\nقالب را انتخاب کن:",
        reply_markup=templates_kb(cat),
    )
    await callback.answer()


@dp.callback_query(F.data == "build_start")
async def cb_build_start(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"🚀 <b>ساخت ربات جدید</b>\n{SEP}\nاول دسته قالب را انتخاب کن:",
        reply_markup=cats_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("tpl:"))
async def cb_tpl(callback: CallbackQuery, state: FSMContext):
    key = callback.data[4:]
    if key not in templates.TEMPLATES:
        return await callback.answer("قالب نامعتبر", show_alert=True)
    label = templates.TEMPLATES[key]
    await state.set_state(Build.brand)
    await state.update_data(template=key, template_label=label)
    await callback.message.edit_text(
        f"✅ قالب: <b>{html.escape(label)}</b>\n{SEP}\n"
        "🏷 <b>نام برند / فروشگاه</b> را بفرست:\n"
        "مثال: <code>VIP Store</code>",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@dp.callback_query(F.data == "cancel_build")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("ساخت لغو شد.", reply_markup=home_kb())
    await callback.answer()


@dp.message(Build.brand)
async def on_brand(message: Message, state: FSMContext):
    brand = (message.text or "").strip()
    if len(brand) < 2:
        return await message.answer("نام برند خیلی کوتاه است.", reply_markup=cancel_kb())
    await state.update_data(brand_name=brand, brand=brand)
    await state.set_state(Build.welcome)
    await message.answer(
        "✉️ متن <b>خوش‌آمدگویی</b> را بفرست:\n"
        "مثال: به فروشگاه ما خوش آمدید",
        reply_markup=cancel_kb(),
    )


@dp.message(Build.welcome)
async def on_welcome(message: Message, state: FSMContext):
    welcome = (message.text or "").strip()
    if len(welcome) < 2:
        return await message.answer("متن خوش‌آمد کوتاه است.", reply_markup=cancel_kb())
    await state.update_data(welcome_text=welcome, welcome=welcome)
    await state.set_state(Build.admin)
    await message.answer(
        "👤 <b>آیدی عددی ادمین</b> را بفرست:\n"
        "از @userinfobot بگیر — فقط عدد",
        reply_markup=cancel_kb(),
    )


@dp.message(Build.admin)
async def on_admin(message: Message, state: FSMContext):
    raw = (message.text or "").strip()
    if not raw.isdigit():
        return await message.answer("فقط عدد آیدی را بفرست.", reply_markup=cancel_kb())
    await state.update_data(admin_id=int(raw))
    data = await state.get_data()
    key = data.get("template") or "shop"
    prompt = templates.detail_prompt(key)
    await state.set_state(Build.detail)
    await message.answer(
        f"🧩 <b>جزئیات قالب</b>\n{SEP}\n{prompt}\n\n"
        "اگر چیزی نداری <code>-</code> بفرست.",
        reply_markup=cancel_kb(),
    )


@dp.message(Build.detail)
async def on_detail(message: Message, state: FSMContext):
    detail = (message.text or "").strip()
    data = await state.get_data()
    await state.clear()
    payload = {
        "template": data.get("template"),
        "brand_name": data.get("brand_name") or data.get("brand"),
        "brand": data.get("brand_name") or data.get("brand"),
        "welcome_text": data.get("welcome_text") or data.get("welcome"),
        "welcome": data.get("welcome_text") or data.get("welcome"),
        "admin_id": data.get("admin_id"),
        "detail": "" if detail == "-" else detail,
    }
    wait = await message.answer("⏳ در حال تولید بسته ربات...")
    try:
        code = templates.build_bot(payload)
        pkg = templates.build_package(payload)
        # inject admin into env example is inside build_package
        fname = f"bot_{(payload.get('brand_name') or 'app').replace(' ', '_')[:24]}.zip"
        await message.answer_document(
            BufferedInputFile(pkg, filename=fname),
            caption=(
                f"✅ <b>ربات آماده شد</b>\n"
                f"قالب: {html.escape(str(data.get('template_label') or payload['template']))}\n"
                f"برند: {html.escape(str(payload.get('brand_name')))}\n"
                f"{SEP}\n"
                "ZIP را روی Railway با PostgreSQL اجرا کن.\n"
                "راهنما داخل README.zip است."
            ),
            reply_markup=home_kb(),
        )
        try:
            await wait.delete()
        except Exception:
            pass
    except Exception as e:
        log.exception("build failed")
        await wait.edit_text(f"❌ خطا در ساخت: <code>{html.escape(str(e))}</code>", reply_markup=home_kb())



@dp.message(F.web_app_data)
async def on_webapp_data(message: Message, state: FSMContext):
    """Receive JSON payload from Mini App via Telegram.sendData."""
    import json
    raw = message.web_app_data.data if message.web_app_data else ""
    try:
        data = json.loads(raw)
    except Exception:
        await message.answer("❌ داده مینی‌اپ نامعتبر بود.", reply_markup=home_kb())
        return
    template = str(data.get("template") or "").strip()
    brand = str(data.get("brand") or data.get("brand_name") or "").strip()
    welcome = str(data.get("welcome") or data.get("welcome_text") or "").strip()
    admin = str(data.get("admin") or data.get("admin_id") or "").strip()
    detail = str(data.get("detail") or "").strip()
    known = set(getattr(templates, "ENGINE_BY_KEY", {}) or {})
    known |= set(getattr(templates, "TEMPLATES", {}) or {})
    known |= set(getattr(templates, "TEMPLATE_META", {}) or {})
    if not template or template not in known:
        await message.answer(
            f"❌ قالب <code>{html.escape(template or '—')}</code> شناخته نشد.\nاز ربات دوباره انتخاب کن.",
            reply_markup=home_kb(),
        )
        return
    if not brand:
        await message.answer("❌ نام برند خالی بود.", reply_markup=home_kb())
        return
    if not admin.isdigit():
        await message.answer("❌ آیدی ادمین نامعتبر است.", reply_markup=home_kb())
        return
    await state.clear()
    payload = {
        "template": template,
        "brand_name": brand,
        "brand": brand,
        "welcome_text": welcome or f"به {brand} خوش آمدید",
        "welcome": welcome or f"به {brand} خوش آمدید",
        "admin_id": int(admin),
        "detail": detail,
    }
    wait = await message.answer(f"⏳ ساخت ربات <b>{html.escape(brand)}</b> از قالب <code>{html.escape(template)}</code>…")
    try:
        pkg = templates.build_package(payload)
        fname = f"bot_{brand.replace(' ', '_')[:24]}.zip"
        label = template
        meta = getattr(templates, "TEMPLATE_META", {}) or {}
        if isinstance(meta.get(template), dict):
            label = meta[template].get("title") or template
        elif template in getattr(templates, "TEMPLATES", {}):
            label = templates.TEMPLATES.get(template) or template
        await message.answer_document(
            BufferedInputFile(pkg, filename=fname),
            caption=(
                f"✅ <b>ربات از مینی‌اپ ساخته شد</b>\n"
                f"قالب: {html.escape(str(label))}\n"
                f"برند: {html.escape(brand)}\n"
                f"{SEP}\n"
                "ZIP را روی Railway اجرا کن."
            ),
            reply_markup=home_kb(),
        )
        try:
            await wait.delete()
        except Exception:
            pass
    except Exception as e:
        log.exception("webapp build failed")
        await wait.edit_text(
            f"❌ خطا: <code>{html.escape(str(e))}</code>",
            reply_markup=home_kb(),
        )


@dp.message()
async def fallback(message: Message):
    await message.answer(
        "از دکمه‌های داخل پیام استفاده کن یا /start بزن.",
        reply_markup=home_kb(),
    )


async def main():
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="شروع کارخانه"),
            BotCommand(command="help", description="راهنما"),
        ]
    )
    log.info("Bot Factory Pro started (inline-only UI)")
    if WEBAPP_URL:
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(
                    text="استودیو",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            )
            log.info("Menu WebApp set: %s", WEBAPP_URL)
        except Exception:
            log.exception("failed to set menu button")
    else:
        log.warning("WEBAPP_URL not set — Mini App button hidden")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
