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
import database as db

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
_admin_raw = (os.getenv("ADMIN_IDS") or os.getenv("ADMIN_ID") or "").replace(" ", "")
ADMIN_IDS = {int(x) for x in _admin_raw.split(",") if x.isdigit()}
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN تنظیم نشده است.")

WEBAPP_URL = (os.getenv("WEBAPP_URL") or os.getenv("MINIAPP_URL") or "").strip().rstrip("/")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("bot_factory")
if WEBAPP_URL and not WEBAPP_URL.startswith(("http://", "https://")):
    log.warning("WEBAPP_URL ignored (need http/https): %s", WEBAPP_URL)
    WEBAPP_URL = ""

# تلگرام WebView را کش می‌کند — با query اجباری نسخه جدید لود می‌شود
WEBAPP_VERSION = "v6"
if WEBAPP_URL:
    sep = "&" if "?" in WEBAPP_URL else "?"
    if f"v={WEBAPP_VERSION}" not in WEBAPP_URL:
        WEBAPP_URL = f"{WEBAPP_URL}{sep}v={WEBAPP_VERSION}"
    log.info("WEBAPP_URL effective: %s", WEBAPP_URL)
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


class AdminFactory(StatesGroup):
    search_user = State()
    broadcast = State()
    set_setting = State()


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


def is_admin(uid: int) -> bool:
    return bool(ADMIN_IDS) and uid in ADMIN_IDS


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
    n_tpl = len(getattr(templates, "TEMPLATES", {}) or {})
    n_cat = len(getattr(templates, "CATEGORIES", {}) or {})
    return (
        "🤖 <b>BOT FACTORY PRO</b>\n"
        "<i>کارخانه ساخت ربات‌های تجاری تلگرام</i>\n"
        f"{SEP}\n"
        f"🚀 <b>{n_tpl} قالب تخصصی</b> در {n_cat} دسته\n"
        "⚡ تولید کد آماده Railway + PostgreSQL\n"
        "🧩 هسته سفارش · رزرو · تیکت · امتیاز\n"
        f"{SEP}\n"
        "از دکمه‌های زیر شروع کن 👇"
        + ("\n✨ مینی‌اپ فعال — از دکمه «استودیو مینی‌اپ» همین پیام باز کن (نه منوی گوشه)." if WEBAPP_URL else "\nℹ️ WEBAPP_URL را برای مینی‌اپ ست کن.")
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
        ("✨ مشاهده همه قالب‌ها", "browse_all"),
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
    if not await db.is_menu_enabled("browse_all"):
        return await callback.answer("این بخش قفل است", show_alert=True)
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





async def guard_user(message_or_cb, user_id: int) -> bool:
    """False if blocked (banned / bot off / maintenance)."""
    try:
        if await db.is_banned(user_id):
            text = "🚫 حساب شما مسدود است."
            if hasattr(message_or_cb, "message"):
                await message_or_cb.answer(text, show_alert=True)
            else:
                await message_or_cb.answer(text)
            return False
        if not await db.is_bot_enabled() and not is_admin(user_id):
            text = "⏸ ربات فعلاً خاموش است."
            if hasattr(message_or_cb, "message"):
                await message_or_cb.answer(text, show_alert=True)
            else:
                await message_or_cb.answer(text)
            return False
        if await db.is_maintenance() and not is_admin(user_id):
            text = "🔧 ربات در حالت تعمیرات است."
            if hasattr(message_or_cb, "message"):
                await message_or_cb.answer(text, show_alert=True)
            else:
                await message_or_cb.answer(text)
            return False
    except Exception:
        log.exception("guard_user")
    return True


def admin_home_kb() -> InlineKeyboardMarkup:
    rows = [
        [("🟢/🔴 ربات", "adm:power"), ("🔧 تعمیرات", "adm:maint")],
        [("👥 کاربران", "adm:users:0"), ("🔎 جستجوی کاربر", "adm:usearch")],
        [("🚫 بن‌شده‌ها", "adm:usersb:0"), ("📊 آمار کامل", "adm:stats")],
        [("📦 قفل قالب‌ها", "adm:tpl:0"), ("📂 قفل دسته‌ها", "adm:cats")],
        [("🎛 قفل منو", "adm:menus"), ("📜 لاگ ساخت‌ها", "adm:blogs")],
        [("📣 پیام همگانی", "adm:bc"), ("⚙️ تنظیمات", "adm:settings")],
        [("✅ فعال‌سازی همه قالب‌ها", "adm:tpl_all_on"), ("❌ قفل همه قالب‌ها", "adm:tpl_all_off")],
        [("✅ باز کردن همه منوها", "adm:menu_all_on"), ("❌ قفل همه منوها", "adm:menu_all_off")],
        [("🏠 خانه کاربر", "home")],
    ]
    kb = []
    for row in rows:
        kb.append([InlineKeyboardButton(text=a, callback_data=b, style=style_for(a, b)) for a, b in row])
    return InlineKeyboardMarkup(inline_keyboard=kb)



@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    try:
        await db.upsert_user(message.from_user.id, message.from_user.username, message.from_user.full_name)
    except Exception:
        log.exception("upsert on start")
    if not await guard_user(message, message.from_user.id):
        return
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
    n_tpl = len(templates.TEMPLATES)
    n_base = sum(len(v) for v in templates.CATEGORIES.values())
    text = (
        "📊 <b>آمار کارخانه</b>\n"
        f"{SEP}\n"
        f"دسته‌ها: <b>{n_cat}</b>\n"
        f"قالب‌ها: <b>{n_tpl}</b>\n"
        f"پایه در دسته‌ها: <b>{n_base}</b> (ساخت از دسته)\n"
        "موتور: PostgreSQL + aiogram 3\n"
        "خروجی: bot.py + requirements + README\n"
    )
    await callback.message.edit_text(text, reply_markup=home_kb())
    await callback.answer()


@dp.callback_query(F.data == "cats")
async def cb_cats(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        f"✨ <b>{len(templates.CATEGORIES)} دسته قالب</b>\n{SEP}\nیک دسته را انتخاب کن (مسیر ساخت از دسته):",
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
    if not await db.is_menu_enabled("build_start"):
        return await callback.answer("این بخش قفل است", show_alert=True)
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
    if not await db.is_template_enabled(key):
        return await callback.answer("این قالب توسط ادمین قفل شده", show_alert=True)
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
        try:
            await db.bump_build(message.from_user.id, payload.get("template") or "", payload.get("brand_name") or payload.get("brand") or "")
        except Exception:
            log.exception("bump_build")
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
    log.info("web_app_data received len=%s from=%s", len(raw or ""), message.from_user.id if message.from_user else None)
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
        try:
            await db.bump_build(message.from_user.id, payload.get("template") or "", payload.get("brand_name") or payload.get("brand") or "")
        except Exception:
            log.exception("bump_build")
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




@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    n_u = await db.count_users()
    n_b = await db.count_builds()
    on = await db.is_bot_enabled()
    maint = await db.is_maintenance()
    await message.answer(
        f"🛠 <b>پنل ادمین کارخانه</b>\n{SEP}\n"
        f"ربات: {'🟢 روشن' if on else '🔴 خاموش'}\n"
        f"تعمیرات: {'🔧 فعال' if maint else '—'}\n"
        f"کاربران: <b>{n_u}</b> · ساخت‌ها: <b>{n_b}</b>\n"
        f"قالب‌ها: <b>{len(templates.TEMPLATES)}</b>\n"
        f"{SEP}\nاز دکمه‌ها مدیریت کن:",
        reply_markup=admin_home_kb(),
    )


@dp.callback_query(F.data.startswith("adm:"))
async def cb_admin_router(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return await callback.answer("دسترسی نداری", show_alert=True)
    data = callback.data
    parts = data.split(":")

    async def refresh_home():
        n_u = await db.count_users()
        n_b = await db.count_builds()
        on = await db.is_bot_enabled()
        maint = await db.is_maintenance()
        await callback.message.edit_text(
            f"🛠 <b>پنل ادمین کارخانه</b>\n{SEP}\n"
            f"ربات: {'🟢 روشن' if on else '🔴 خاموش'}\n"
            f"تعمیرات: {'🔧 فعال' if maint else '—'}\n"
            f"کاربران: <b>{n_u}</b> · ساخت‌ها: <b>{n_b}</b>\n"
            f"قالب‌ها: <b>{len(templates.TEMPLATES)}</b>",
            reply_markup=admin_home_kb(),
        )

    # power toggle
    if data == "adm:power":
        on = await db.is_bot_enabled()
        await db.set_bot_enabled(not on)
        await callback.answer("روشن شد ✅" if not on else "خاموش شد ⏸", show_alert=True)
        return await refresh_home()

    if data == "adm:maint":
        m = await db.is_maintenance()
        await db.set_maintenance(not m)
        await callback.answer("تعمیرات روشن" if not m else "تعمیرات خاموش", show_alert=True)
        return await refresh_home()

    if data == "adm:home":
        await state.clear()
        return await refresh_home()

    if data == "adm:stats":
        n_u = await db.count_users()
        n_ban = await db.count_users(only_banned=True)
        n_b = await db.count_builds()
        n_tpl = len(templates.TEMPLATES)
        n_cat = len(templates.CATEGORIES)
        await callback.message.edit_text(
            f"📊 <b>آمار کامل</b>\n{SEP}\n"
            f"کاربران: <b>{n_u}</b>\nبن‌شده: <b>{n_ban}</b>\n"
            f"ساخت ZIP: <b>{n_b}</b>\nقالب: <b>{n_tpl}</b>\nدسته: <b>{n_cat}</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ پنل ادمین", callback_data="adm:home", style="primary")]
            ]),
        )
        return await callback.answer()

    if data.startswith("adm:users:") or data.startswith("adm:usersb:"):
        banned_only = data.startswith("adm:usersb:")
        try:
            page = int(parts[2])
        except Exception:
            page = 0
        users = await db.users_page(page, 8, only_banned=banned_only)
        total = await db.count_users(only_banned=banned_only)
        pages = max(1, (total + 7) // 8)
        lines = [f"{'🚫 بن‌شده‌ها' if banned_only else '👥 کاربران'} — صفحه {page+1}/{pages}\n{SEP}"]
        rows = []
        for u in users:
            un = f"@{u['username']}" if u.get("username") else "—"
            flag = "🚫" if u.get("is_banned") else "✅"
            lines.append(f"{flag} <code>{u['user_id']}</code> {html.escape(u.get('full_name') or '—')} {un}")
            rows.append([InlineKeyboardButton(
                text=f"{flag} {u['user_id']}",
                callback_data=f"adm:user:{u['user_id']}",
                style="danger" if u.get("is_banned") else "primary",
            )])
        nav = []
        prefix = "adm:usersb" if banned_only else "adm:users"
        if page > 0:
            nav.append(InlineKeyboardButton(text="◀️", callback_data=f"{prefix}:{page-1}", style="primary"))
        if page < pages - 1:
            nav.append(InlineKeyboardButton(text="▶️", callback_data=f"{prefix}:{page+1}", style="primary"))
        if nav:
            rows.append(nav)
        rows.append([InlineKeyboardButton(text="↩️ پنل ادمین", callback_data="adm:home", style="primary")])
        await callback.message.edit_text("\n".join(lines) if len(lines) > 1 else lines[0] + "\nخالی", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
        return await callback.answer()

    if data.startswith("adm:user:"):
        uid = int(parts[2])
        u = await db.get_user(uid)
        if not u:
            return await callback.answer("کاربر نیست", show_alert=True)
        un = f"@{u['username']}" if u.get("username") else "—"
        text = (
            f"👤 <b>کاربر</b>\n{SEP}\n"
            f"آیدی: <code>{uid}</code>\n"
            f"نام: {html.escape(u.get('full_name') or '—')}\n"
            f"یوزرنیم: {un}\n"
            f"بن: {'بله' if u.get('is_banned') else 'خیر'}\n"
            f"تعداد ساخت: {u.get('builds_count') or 0}\n"
            f"آخرین قالب: <code>{html.escape(u.get('last_template') or '—')}</code>"
        )
        ban_btn = ("✅ آنبن", f"adm:unban:{uid}") if u.get("is_banned") else ("🚫 بن", f"adm:ban:{uid}")
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=ban_btn[0], callback_data=ban_btn[1], style="danger" if not u.get("is_banned") else "success")],
            [InlineKeyboardButton(text="↩️ لیست", callback_data="adm:users:0", style="primary")],
            [InlineKeyboardButton(text="🛠 پنل ادمین", callback_data="adm:home", style="primary")],
        ])
        await callback.message.edit_text(text, reply_markup=kb)
        return await callback.answer()

    if data.startswith("adm:ban:"):
        uid = int(parts[2])
        await db.set_banned(uid, True)
        await callback.answer("بن شد", show_alert=True)
        callback.data = f"adm:user:{uid}"
        return await cb_admin_router(callback, state)

    if data.startswith("adm:unban:"):
        uid = int(parts[2])
        await db.set_banned(uid, False)
        await callback.answer("آنبن شد", show_alert=True)
        callback.data = f"adm:user:{uid}"
        return await cb_admin_router(callback, state)

    if data == "adm:usearch":
        await state.set_state(AdminFactory.search_user)
        await callback.message.edit_text(
            f"🔎 آیدی عددی یا یوزرنیم یا نام را بفرست:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ انصراف", callback_data="adm:home", style="danger")]
            ]),
        )
        return await callback.answer()

    if data.startswith("adm:tpl:"):
        try:
            page = int(parts[2])
        except Exception:
            page = 0
        items = list(templates.TEMPLATES.items())
        per = 8
        total = len(items)
        pages = max(1, (total + per - 1) // per)
        page = max(0, min(page, pages - 1))
        chunk = items[page * per : (page + 1) * per]
        rows = []
        lines = [f"📦 قفل/باز قالب‌ها — {page+1}/{pages}\n{SEP}"]
        for key, label in chunk:
            en = await db.is_template_enabled(key)
            icon = "🟢" if en else "🔴"
            lines.append(f"{icon} {html.escape(str(label)[:40])}")
            rows.append([InlineKeyboardButton(
                text=f"{icon} {str(label)[:28]}",
                callback_data=f"adm:ttog:{key}"[:64],
                style="success" if en else "danger",
            )])
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton(text="◀️", callback_data=f"adm:tpl:{page-1}", style="primary"))
        if page < pages - 1:
            nav.append(InlineKeyboardButton(text="▶️", callback_data=f"adm:tpl:{page+1}", style="primary"))
        if nav:
            rows.append(nav)
        rows.append([InlineKeyboardButton(text="↩️ پنل", callback_data="adm:home", style="primary")])
        await callback.message.edit_text("\n".join(lines[:12]), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
        return await callback.answer()

    if data.startswith("adm:ttog:"):
        key = data[9:]  # adm:ttog:KEY
        en = await db.is_template_enabled(key)
        await db.set_template_enabled(key, not en)
        await callback.answer("باز شد" if not en else "قفل شد", show_alert=True)
        # stay on page 0 for simplicity
        callback.data = "adm:tpl:0"
        return await cb_admin_router(callback, state)

    if data == "adm:tpl_all_on":
        for key in templates.TEMPLATES:
            await db.set_template_enabled(key, True)
        await callback.answer("همه قالب‌ها فعال", show_alert=True)
        return await refresh_home()

    if data == "adm:tpl_all_off":
        for key in templates.TEMPLATES:
            await db.set_template_enabled(key, False)
        await callback.answer("همه قالب‌ها قفل", show_alert=True)
        return await refresh_home()

    if data == "adm:cats":
        rows = []
        for cat in templates.CATEGORIES:
            en = await db.is_category_enabled(cat)
            icon = "🟢" if en else "🔴"
            # callback must be short — use index
            rows.append([InlineKeyboardButton(
                text=f"{icon} {cat[:40]}",
                callback_data=f"adm:ctog:{list(templates.CATEGORIES.keys()).index(cat)}",
                style="success" if en else "danger",
            )])
        rows.append([InlineKeyboardButton(text="↩️ پنل", callback_data="adm:home", style="primary")])
        await callback.message.edit_text(f"📂 قفل دسته‌ها\n{SEP}", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
        return await callback.answer()

    if data.startswith("adm:ctog:"):
        idx = int(parts[2])
        cat = list(templates.CATEGORIES.keys())[idx]
        en = await db.is_category_enabled(cat)
        await db.set_category_enabled(cat, not en)
        await callback.answer("باز شد" if not en else "قفل شد", show_alert=True)
        callback.data = "adm:cats"
        return await cb_admin_router(callback, state)

    if data == "adm:menus":
        menus = [
            ("build_start", "ساخت ربات جدید"),
            ("browse_all", "مشاهده قالب‌ها"),
            ("stats", "آمار"),
            ("guide", "آموزش"),
            ("webapp", "مینی‌اپ"),
        ]
        rows = []
        for key, title in menus:
            en = await db.is_menu_enabled(key)
            icon = "🟢" if en else "🔴"
            rows.append([InlineKeyboardButton(
                text=f"{icon} {title}",
                callback_data=f"adm:mtog:{key}",
                style="success" if en else "danger",
            )])
        rows.append([InlineKeyboardButton(text="↩️ پنل", callback_data="adm:home", style="primary")])
        await callback.message.edit_text(f"🎛 قفل دکمه‌های منو\n{SEP}", reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
        return await callback.answer()

    if data.startswith("adm:mtog:"):
        key = parts[2]
        en = await db.is_menu_enabled(key)
        await db.set_menu_enabled(key, not en)
        await callback.answer("باز شد" if not en else "قفل شد", show_alert=True)
        callback.data = "adm:menus"
        return await cb_admin_router(callback, state)

    if data == "adm:menu_all_on":
        for k in ("build_start", "browse_all", "stats", "guide", "webapp"):
            await db.set_menu_enabled(k, True)
        await callback.answer("منوها باز", show_alert=True)
        return await refresh_home()

    if data == "adm:menu_all_off":
        for k in ("build_start", "browse_all", "stats", "guide", "webapp"):
            await db.set_menu_enabled(k, False)
        await callback.answer("منوها قفل", show_alert=True)
        return await refresh_home()

    if data == "adm:blogs":
        logs = await db.recent_builds(12)
        lines = [f"📜 آخرین ساخت‌ها\n{SEP}"]
        for L in logs:
            lines.append(f"#{L['id']} u<code>{L['user_id']}</code> · <code>{html.escape(L.get('template_key') or '')}</code> · {html.escape(L.get('brand') or '')}")
        if len(lines) == 1:
            lines.append("خالی")
        await callback.message.edit_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ پنل", callback_data="adm:home", style="primary")]
            ]),
        )
        return await callback.answer()

    if data == "adm:bc":
        await state.set_state(AdminFactory.broadcast)
        await callback.message.edit_text(
            "📣 متن پیام همگانی را بفرست:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ انصراف", callback_data="adm:home", style="danger")]
            ]),
        )
        return await callback.answer()

    if data == "adm:settings":
        on = await db.is_bot_enabled()
        maint = await db.is_maintenance()
        await callback.message.edit_text(
            f"⚙️ <b>تنظیمات</b>\n{SEP}\n"
            f"ربات: {'روشن' if on else 'خاموش'}\n"
            f"تعمیرات: {'بله' if maint else 'خیر'}\n"
            f"WEBAPP: <code>{html.escape(WEBAPP_URL or '—')}</code>\n"
            f"ادمین‌ها: <code>{html.escape(','.join(str(x) for x in sorted(ADMIN_IDS)) or '—')}</code>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🟢/🔴 ربات", callback_data="adm:power", style="success")],
                [InlineKeyboardButton(text="🔧 تعمیرات", callback_data="adm:maint", style="primary")],
                [InlineKeyboardButton(text="↩️ پنل", callback_data="adm:home", style="primary")],
            ]),
        )
        return await callback.answer()

    await callback.answer()


@dp.message(AdminFactory.search_user)
async def on_admin_search(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    users = await db.find_users(message.text or "")
    await state.clear()
    if not users:
        await message.answer("پیدا نشد.", reply_markup=admin_home_kb())
        return
    rows = []
    lines = [f"🔎 نتایج\n{SEP}"]
    for u in users[:12]:
        lines.append(f"<code>{u['user_id']}</code> {html.escape(u.get('full_name') or '—')}")
        rows.append([InlineKeyboardButton(text=str(u['user_id']), callback_data=f"adm:user:{u['user_id']}", style="primary")])
    rows.append([InlineKeyboardButton(text="↩️ پنل", callback_data="adm:home", style="primary")])
    await message.answer("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@dp.message(AdminFactory.broadcast)
async def on_admin_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    text = message.text or message.caption or ""
    if not text.strip():
        await message.answer("متن خالی بود.")
        return
    await state.clear()
    # broadcast to known users
    page = 0
    sent = 0
    fail = 0
    while True:
        users = await db.users_page(page, 50)
        if not users:
            break
        for u in users:
            if u.get("is_banned"):
                continue
            try:
                await bot.send_message(u["user_id"], text)
                sent += 1
            except Exception:
                fail += 1
        page += 1
        if page > 200:
            break
    await message.answer(f"📣 ارسال شد: {sent} · ناموفق: {fail}", reply_markup=admin_home_kb())



@dp.message()
async def fallback(message: Message):
    await message.answer(
        "از دکمه‌های داخل پیام استفاده کن یا /start بزن.",
        reply_markup=home_kb(),
    )


async def main():
    await db.init_db()
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
