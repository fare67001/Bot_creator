# -*- coding: utf-8 -*-
"""Bot Factory Pro — builder bot for 100 Telegram bot templates."""
from __future__ import annotations
import asyncio
import html
import logging
from io import BytesIO

from aiogram import Bot, Dispatcher, F
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
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Message,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

import templates

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN تنظیم نشده است. فایل .env را تنظیم کنید.")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bot_factory")
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
SEP = "━━━━━━━━━━━━━━━━"


class Build(StatesGroup):
    choosing = State()
    brand = State()
    welcome = State()
    admin = State()
    detail = State()


def button_style(text: str, callback_data: str) -> str:
    """رنگ دکمه‌ها را بر اساس نوع عمل تعیین می‌کند؛ منطق ربات دست‌نخورده می‌ماند."""
    danger_words = ("لغو", "حذف", "رد", "danger")
    success_words = ("ساخت ربات جدید", "شروع ساخت", "تأیید", "فعال", "شروع")
    if callback_data == "cancel" or any(word in text for word in danger_words):
        return "danger"
    if any(word in text for word in success_words):
        return "success"
    return "primary"


def grid(rows: list[tuple[str, str]], columns: int = 2) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, len(rows), columns):
        keyboard.append([
            InlineKeyboardButton(
                text=t,
                callback_data=c,
                style=button_style(t, c),
            )
            for t, c in rows[i:i+columns]
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def one_col(rows: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    return grid(rows, 1)


def reply_grid(labels: list[str], columns: int = 2, placeholder: str = "انتخاب کن…") -> ReplyKeyboardMarkup:
    rows = []
    for i in range(0, len(labels), columns):
        rows.append([KeyboardButton(text=x, style=button_style(x, None)) for x in labels[i:i+columns]])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        is_persistent=True,
        input_field_placeholder=placeholder,
    )


def home_reply_kb() -> ReplyKeyboardMarkup:
    return reply_grid([
        "🚀 ساخت ربات جدید", "✨ مشاهده ۱۰۰ قالب",
        "📊 آمار کارخانه", "🎓 آموزش راه‌اندازی",
    ], 2, "یک گزینه را انتخاب کن…")


def categories_reply_kb() -> ReplyKeyboardMarkup:
    labels = list(templates.CATEGORIES)
    labels += ["✨ نمایش همه ۱۰۰ قالب", "🎓 آموزش راه‌اندازی", "🏠 خانه"]
    return reply_grid(labels, 2, "دسته یا قالب را انتخاب کن…")


def templates_reply_kb(category_index: int) -> ReplyKeyboardMarkup:
    category = list(templates.CATEGORIES)[category_index]
    labels = [label for _, label in templates.CATEGORIES[category]]
    labels += ["🔙 دسته‌ها", "🎓 آموزش راه‌اندازی", "🏠 خانه"]
    return reply_grid(labels, 2, "یک قالب را انتخاب کن…")


def all_templates_reply_kb(page: int = 0) -> ReplyKeyboardMarkup:
    items = list(templates.TEMPLATES.items())
    page_size = 20
    page_count = (len(items) + page_size - 1) // page_size
    page = max(0, min(page, page_count - 1))
    labels = [label for _, label in items[page * page_size:(page + 1) * page_size]]
    nav = []
    if page > 0:
        nav.append("⬅️ قبلی")
    if page < page_count - 1:
        nav.append("بعدی ➡️")
    labels += nav + ["🔙 دسته‌ها", "🎓 آموزش راه‌اندازی", "🏠 خانه"]
    return reply_grid(labels, 2, f"قالب‌ها — صفحه {page + 1}/{page_count}")


def cancel_reply_kb() -> ReplyKeyboardMarkup:
    return reply_grid(["🔴 لغو ساخت", "🎓 آموزش راه‌اندازی"], 1, "در حال ساخت…")


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def categories_kb() -> InlineKeyboardMarkup:
    rows = [(name, f"cat:{i}") for i, name in enumerate(templates.CATEGORIES)]
    rows += [("✨ نمایش همه ۱۰۰ قالب", "all:0"), ("ℹ️ راهنما", "help_ui")]
    return grid(rows, 2)


def templates_kb(index: int) -> InlineKeyboardMarkup:
    category = list(templates.CATEGORIES)[index]
    rows = [(label, f"tpl:{key}") for key, label in templates.CATEGORIES[category]]
    rows += [("🔙 دسته‌ها", "cats"), ("🏠 خانه", "home")]
    return grid(rows, 2)


def all_templates_kb(page: int = 0) -> InlineKeyboardMarkup:
    items = list(templates.TEMPLATES.items())
    page_size = 20
    page_count = (len(items) + page_size - 1) // page_size
    page = max(0, min(page, page_count - 1))
    chunk = items[page * page_size:(page + 1) * page_size]
    rows = [(label, f"tpl:{key}") for key, label in chunk]
    nav = []
    if page > 0:
        nav.append(("⬅️ قبلی", f"all:{page-1}"))
    if page < page_count - 1:
        nav.append(("بعدی ➡️", f"all:{page+1}"))
    if nav:
        rows.extend(nav)
    rows.append(("🔙 دسته‌ها", "cats"))
    return grid(rows, 2)


def home_text() -> str:
    return (
        "🤖 <b>BOT FACTORY PRO</b>\n"
        "<i>کارخانه ساخت ربات‌های حرفه‌ای تلگرام</i>\n"
        + SEP + "\n"
        "🚀 <b>100 قالب آماده</b> | ⚡ تولید سریع | 🧩 قابل شخصی‌سازی\n\n"
        "از فروشگاه و رزرو تا آموزش، پشتیبانی، جامعه، محتوا و ابزارهای کاربردی.\n\n"
        "👇 برای شروع یک دسته را انتخاب کن:"
    )


def home_kb() -> InlineKeyboardMarkup:
    return grid([
        ("🚀 ساخت ربات جدید", "cats"),
        ("✨ مشاهده ۱۰۰ قالب", "all:0"),
        ("📊 آمار کارخانه", "stats"),
        ("ℹ️ راهنمای استفاده", "help_ui"),
    ], 2)


def cancel_kb() -> InlineKeyboardMarkup:
    return one_col([("🔴 لغو ساخت", "cancel")])

def detail_prompt(key: str) -> str:
    meta = templates.TEMPLATE_META[key]
    kind = meta["kind"]
    examples = {
        "catalog_price": "هر مورد: عنوان | قیمت | توضیح\nمثال: محصول A | 250000 | توضیحات محصول",
        "catalog": "هر مورد: عنوان | توضیح\nمثال: خدمت A | توضیحات خدمت",
        "membership": "هر پلن: عنوان | قیمت | توضیح\nمثال: VIP ماهانه | 500000 | امکانات پلن",
        "booking": "هر زمان در یک خط\nمثال: شنبه 18:00\nیکشنبه 10:30",
        "quiz": "هر سوال: سوال | گزینه۱,گزینه۲,گزینه۳ | شماره گزینه صحیح",
        "poll": "یک خط: سوال | گزینه۱,گزینه۲,گزینه۳",
        "links": "هر لینک: عنوان | https://example.com",
        "file_store": "هر فایل: عنوان | file_id تلگرام",
        "content": "هر مطلب: عنوان | متن مطلب",
        "channel": "یوزرنیم کانال مثل @mychannel",
        "rules": "متن کامل قوانین را بفرست.",
        "form": "نام فیلدهای فرم را با کاما جدا کن؛ مثال: نام, شماره تماس, توضیحات",
        "feedback": "نام فیلدها را با کاما جدا کن؛ مثال: امتیاز, نظر, پیشنهاد",
        "event": "هر رویداد: عنوان | توضیح\nمثال: ورکشاپ تابستانی | توضیحات و زمان برگزاری",
        "coupon": "کدها را با کاما جدا کن؛ مثال: VIP20, NEW10, WELCOME",
        "donation": "متن هدف کمپین یا توضیح حمایت را بفرست.",
    }
    return "4️⃣ <b>اطلاعات اختصاصی قالب</b> را بفرست:\n\n" + examples.get(kind, "/empty برای مقدار پیش‌فرض")


def parse_lines(raw: str) -> list[str]:
    return [x.strip() for x in raw.splitlines() if x.strip()]


def parse_catalog(raw: str, with_price: bool) -> list[dict]:
    items: list[dict] = []
    for line in parse_lines(raw):
        parts = [p.strip() for p in line.split("|", 2)]
        if len(parts) < 2:
            continue
        if with_price:
            if len(parts) < 3:
                items.append({"name": parts[0], "title": parts[0], "price": parts[1], "desc": ""})
            else:
                items.append({"name": parts[0], "title": parts[0], "price": parts[1], "desc": parts[2]})
        else:
            items.append({"name": parts[0], "title": parts[0], "desc": parts[1], "text": parts[1]})
    return items


def parse_detail(key: str, raw: str) -> dict:
    raw = raw.strip()
    if raw == "/empty":
        raw = ""
    kind = templates.TEMPLATE_META[key]["kind"]
    if kind == "catalog_price":
        return {"items": parse_catalog(raw, True)}
    if kind in {"catalog", "membership"}:
        return {"items": parse_catalog(raw, kind == "membership")}
    if kind == "event":
        return {"items": parse_catalog(raw, False)}
    if kind == "booking":
        return {"slots": parse_lines(raw)}
    if kind == "quiz":
        questions = []
        for line in parse_lines(raw):
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) != 3:
                continue
            options = [x.strip() for x in parts[1].split(",") if x.strip()]
            try:
                correct = int(parts[2]) - 1
            except ValueError:
                continue
            if options and 0 <= correct < len(options):
                questions.append({"q": parts[0], "options": options, "correct": correct})
        return {"questions": questions}
    if kind == "poll":
        parts = [p.strip() for p in raw.split("|", 1)]
        return {
            "question": parts[0] if parts and parts[0] else "نظرت چیست؟",
            "options": [x.strip() for x in parts[1].split(",") if x.strip()] if len(parts) == 2 else [],
        }
    if kind == "links":
        links = []
        for line in parse_lines(raw):
            parts = line.split("|", 1)
            if len(parts) == 2:
                links.append({"title": parts[0].strip(), "url": parts[1].strip()})
        return {"links": links}
    if kind == "file_store":
        files = []
        for line in parse_lines(raw):
            parts = line.split("|", 1)
            if len(parts) == 2:
                files.append({"title": parts[0].strip(), "file_id": parts[1].strip()})
        return {"files": files}
    if kind == "content":
        items = []
        for line in parse_lines(raw):
            parts = line.split("|", 1)
            if len(parts) == 2:
                items.append({"title": parts[0].strip(), "text": parts[1].strip()})
        return {"items": items}
    if kind == "channel":
        channel = raw or "@yourchannel"
        return {"channel": channel if channel.startswith("@") else "@" + channel}
    if kind == "rules":
        return {"rules": raw}
    if kind in {"form", "feedback"}:
        return {"fields": [x.strip() for x in raw.split(",") if x.strip()]}
    if kind == "faq":
        items = []
        for line in parse_lines(raw):
            parts = line.split("|", 1)
            if len(parts) == 2:
                items.append({"q": parts[0].strip(), "a": parts[1].strip()})
        return {"items": items}
    if kind == "faq":
        items = []
        for line in parse_lines(raw):
            parts = line.split("|", 1)
            if len(parts) == 2:
                items.append({"q": parts[0].strip(), "a": parts[1].strip()})
        return {"items": items}
    if kind == "coupon":
        return {"coupons": [x.strip() for x in raw.split(",") if x.strip()]}
    if kind == "donation":
        return {"campaign": raw}
    return {"detail": raw}


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Build.choosing)
    await state.update_data(all_page=0)
    await message.answer(home_text(), reply_markup=home_reply_kb())


@dp.callback_query(F.data == "home")
async def home(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await call.message.edit_text(home_text())
    await call.message.answer("🏠 منوی اصلی", reply_markup=home_reply_kb())


@dp.callback_query(F.data == "stats")
async def stats(call: CallbackQuery):
    await call.answer()
    categories = len(templates.CATEGORIES)
    await call.message.edit_text(
        "📊 <b>آمار Bot Factory Pro</b>\n" + SEP + "\n"
        f"🧩 قالب‌ها: <b>{len(templates.TEMPLATES)}</b>\n"
        f"📚 دسته‌ها: <b>{categories}</b>\n"
        "⚡ خروجی: <code>bot.py</code> مستقل\n"
        "🛡️ اعتبارسنجی: Compile قبل از تحویل\n\n"
        "ساختار پروژه برای اضافه‌شدن قالب‌های بیشتر آماده است.",
        reply_markup=one_col([("🔙 برگشت", "home")]),
    )


@dp.callback_query(F.data == "help_ui")
async def help_ui(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(
        "ℹ️ <b>چطور ربات بسازم؟</b>\n" + SEP + "\n"
        "1️⃣ یک قالب انتخاب کن\n"
        "2️⃣ نام برند را وارد کن\n"
        "3️⃣ پیام خوش‌آمدگویی را بنویس\n"
        "4️⃣ آیدی عددی ادمین را بده\n"
        "5️⃣ اطلاعات اختصاصی قالب را وارد کن\n\n"
        "🎉 در پایان فایل مستقل <code>bot.py</code> را دریافت می‌کنی.",
        reply_markup=one_col([("🚀 شروع ساخت", "cats"), ("🏠 خانه", "home")]),
    )


@dp.callback_query(F.data.startswith("all:"))
async def all_templates(call: CallbackQuery):
    page = int(call.data.split(":", 1)[1])
    await call.answer()
    await call.message.edit_text(
        f"✨ <b>همه قالب‌ها</b> — صفحه {page + 1}/5\n" + SEP + "\n"
        "یک ربات را برای ساخت انتخاب کن:"
    )
    await call.message.answer("👇 قالب‌ها", reply_markup=all_templates_reply_kb(page))


@dp.message(F.text == "🎓 آموزش راه‌اندازی")
async def deployment_guide(message: Message):
    await message.answer(
        "🎓 <b>آموزش کامل راه‌اندازی ربات</b>\n" + SEP + "\n"
        "این راهنما برای تمام ربات‌هایی است که از Bot Factory Pro می‌سازی.\n\n"
        "<b>1️⃣ فایل ربات را دریافت کن</b>\n"
        "بعد از ساخت، فایل <code>bot.py</code> را از همین ربات دریافت می‌کنی.\n\n"
        "<b>2️⃣ ساخت Repository در GitHub</b>\n"
        "در GitHub یک Repository جدید بساز و فایل <code>bot.py</code> را داخل ریشه آن آپلود کن.\n"
        "اگر رباتت فایل‌های بیشتری داشت، همه فایل‌های پروژه را در همان Repository قرار بده.\n"
        "فایل <code>.env</code> و توکن واقعی ربات را روی GitHub آپلود نکن.\n\n"
        "<b>3️⃣ requirements.txt</b>\n"
        "اگر فایل <code>requirements.txt</code> در پروژه هست، همان را آپلود کن.\n"
        "برای قالب‌های این کارخانه معمولاً وابستگی‌های موردنیاز داخل همین فایل مشخص شده‌اند.\n\n"
        "<b>4️⃣ ساخت پروژه در Railway</b>\n"
        "وارد Railway شو → پروژه جدید بساز → گزینه Deploy from GitHub Repo را انتخاب کن → Repository رباتت را انتخاب کن.\n\n"
        "<b>5️⃣ متغیرهای محیطی (Variables)</b>\n"
        "در Railway → Service → Variables، توکن ربات را قرار بده:\n\n"
        "<code>BOT_TOKEN = توکن ربات از BotFather</code>\n\n"
        "اگر رباتت قابلیت ادمین دارد، این مورد را هم قرار بده:\n"
        "<code>ADMIN_ID = آیدی عددی ادمین</code>\n\n"
        "⚠️ مقدار توکن را داخل کد یا GitHub قرار نده؛ فقط در Variables ریلوی بگذار.\n\n"
        "<b>6️⃣ Start Command</b>\n"
        "اگر Railway خودش فرمان اجرا را تشخیص نداد، در Service Settings → Start Command بنویس:\n\n"
        "<code>python bot.py</code>\n\n"
        "<b>7️⃣ Deploy و بررسی Logs</b>\n"
        "بعد از ذخیره Variables، Deploy را انجام بده و Logs را بررسی کن.\n"
        "اگر پیام شروع polling یا اجرای موفق برنامه را دیدی، ربات باید آنلاین باشد.\n\n"
        "<b>8️⃣ نکته مهم درباره چند ربات</b>\n"
        "هر رباتی که می‌سازی یک BOT_TOKEN مستقل دارد. برای هر ربات، Repository و/یا Service جداگانه داشته باش یا پروژه را با تنظیمات مستقل اجرا کن.\n\n"
        "<b>❌ خطاهای رایج</b>\n"
        "• BOT_TOKEN تنظیم نشده → Variable را بررسی کن.\n"
        "• ربات آنلاین نیست → Logs را بررسی کن.\n"
        "• ModuleNotFoundError → requirements.txt را بررسی و Deploy مجدد کن.\n"
        "• اجرای اشتباه فایل → Start Command را روی <code>python bot.py</code> بگذار.\n"
        "• توکن اشتباه → توکن جدید را از BotFather بررسی کن.\n\n"
        "<b>✅ چک‌لیست نهایی</b>\n"
        "☑️ bot.py در GitHub\n"
        "☑️ requirements.txt در GitHub\n"
        "☑️ BOT_TOKEN در Railway Variables\n"
        "☑️ ADMIN_ID در صورت نیاز\n"
        "☑️ Start Command درست\n"
        "☑️ Deploy موفق\n"
        "☑️ بررسی Logs\n\n"
        "💡 اگر همه این موارد درست باشند، ربات آماده استفاده است.",
        reply_markup=home_reply_kb(),
    )

@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "ℹ️ <b>راهنمای Bot Factory Pro</b>\n" + SEP + "\n"
        "/start — 🏠 صفحه اصلی\n"
        "/templates — ✨ لیست ۱۰۰ قالب\n"
        "/cancel — 🔴 لغو ساخت فعلی\n\n"
        "با انتخاب قالب، ربات‌ساز مرحله‌به‌مرحله تنظیمات لازم را می‌گیرد و در پایان فایل مستقل <code>bot.py</code> تحویل می‌دهد."
    )


@dp.message(Command("templates"))
async def templates_cmd(message: Message, state: FSMContext):
    await state.set_state(Build.choosing)
    await state.update_data(all_page=0)
    await message.answer(
        "✨ <b>۱۰۰ قالب حرفه‌ای</b>\n" + SEP + "\nیک قالب را انتخاب کن:",
        reply_markup=all_templates_reply_kb(0),
    )


@dp.message(Command("cancel"))
async def cancel_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔴 ساخت لغو شد. برای شروع دوباره /start را بزن.")


@dp.callback_query(F.data == "cancel")
async def cancel_callback(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer()
    await call.message.answer("🔴 ساخت لغو شد. برای شروع دوباره /start را بزن.")


@dp.callback_query(Build.choosing, F.data == "cats")
async def categories(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("📚 <b>دسته‌بندی قالب‌ها</b>\nیک دسته را انتخاب کن:")
    await call.message.answer("📚 انتخاب دسته", reply_markup=categories_reply_kb())


@dp.callback_query(Build.choosing, F.data.startswith("cat:"))
async def category(call: CallbackQuery):
    index = int(call.data.split(":", 1)[1])
    names = list(templates.CATEGORIES)
    if not 0 <= index < len(names):
        return await call.answer("دسته نامعتبر است.", show_alert=True)
    await call.answer()
    name = names[index]
    await call.message.edit_text(f"✨ <b>{html.escape(name)}</b>\n" + SEP + "\nیک قالب حرفه‌ای را انتخاب کن:")
    await call.message.answer("👇 قالب موردنظر را انتخاب کن", reply_markup=templates_reply_kb(index))


def template_key_by_label(text: str) -> str | None:
    for key, label in templates.TEMPLATES.items():
        if label == text:
            return key
    return None


@dp.message(Build.choosing, F.text == "🚀 ساخت ربات جدید")
async def menu_build(message: Message, state: FSMContext):
    await message.answer("📚 <b>دسته‌بندی قالب‌ها</b>\nیک دسته را انتخاب کن:", reply_markup=categories_reply_kb())


@dp.message(Build.choosing, F.text == "✨ مشاهده ۱۰۰ قالب")
async def menu_all(message: Message, state: FSMContext):
    await message.answer("✨ <b>همه قالب‌ها</b> — صفحه 1/5\n" + SEP + "\nیک ربات را برای ساخت انتخاب کن:", reply_markup=all_templates_reply_kb(0))


@dp.message(Build.choosing, F.text == "📊 آمار کارخانه")
async def menu_stats(message: Message):
    await message.answer(
        "📊 <b>آمار Bot Factory Pro</b>\n" + SEP + "\n"
        f"🧩 قالب‌ها: <b>{len(templates.TEMPLATES)}</b>\n"
        f"📚 دسته‌ها: <b>{len(templates.CATEGORIES)}</b>\n"
        "⚡ خروجی: <code>bot.py</code> مستقل\n"
        "🛡️ اعتبارسنجی: Compile قبل از تحویل",
        reply_markup=home_reply_kb(),
    )



@dp.message(Build.choosing, F.text == "🏠 خانه")
async def menu_home(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(home_text(), reply_markup=home_reply_kb())


@dp.message(Build.choosing, F.text == "🔙 دسته‌ها")
async def menu_categories(message: Message):
    await message.answer("📚 <b>دسته‌بندی قالب‌ها</b>\nیک دسته را انتخاب کن:", reply_markup=categories_reply_kb())


@dp.message(Build.choosing, F.text == "✨ نمایش همه ۱۰۰ قالب")
async def menu_all_alias(message: Message, state: FSMContext):
    await state.update_data(all_page=0)
    await message.answer("✨ <b>همه قالب‌ها</b> — صفحه 1/5", reply_markup=all_templates_reply_kb(0))


@dp.message(Build.choosing, F.text == "⬅️ قبلی")
async def menu_prev(message: Message, state: FSMContext):
    data = await state.get_data()
    page = max(0, int(data.get("all_page", 0)) - 1)
    await state.update_data(all_page=page)
    await message.answer(f"✨ <b>همه قالب‌ها</b> — صفحه {page + 1}/5", reply_markup=all_templates_reply_kb(page))


@dp.message(Build.choosing, F.text == "بعدی ➡️")
async def menu_next(message: Message, state: FSMContext):
    data = await state.get_data()
    page = min(4, int(data.get("all_page", 0)) + 1)
    await state.update_data(all_page=page)
    await message.answer(f"✨ <b>همه قالب‌ها</b> — صفحه {page + 1}/5", reply_markup=all_templates_reply_kb(page))


@dp.message(Build.choosing)
async def choose_category_or_template_by_text(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    category_names = list(templates.CATEGORIES)
    if text in category_names:
        index = category_names.index(text)
        await state.update_data(category_index=index)
        await message.answer(f"✨ <b>{html.escape(text)}</b>\n" + SEP + "\nیک قالب حرفه‌ای را انتخاب کن:", reply_markup=templates_reply_kb(index))
        return
    if text == "🏠 خانه":
        await state.clear()
        await message.answer(home_text(), reply_markup=home_reply_kb())
        return
    key = template_key_by_label(text)
    if not key:
        return
    await state.update_data(template=key)
    await state.set_state(Build.brand)
    await message.answer(
        f"✅ <b>{html.escape(templates.TEMPLATES[key])}</b>\n\n1️⃣ نام برند یا نام ربات را بفرست:",
        reply_markup=cancel_reply_kb(),
    )


@dp.message(Build.choosing, F.text == "ℹ️ راهنما")
async def menu_help_short(message: Message):
    await message.answer("ℹ️ برای ساخت، یک قالب را انتخاب کن؛ سپس اطلاعات مرحله‌به‌مرحله دریافت می‌شود.", reply_markup=home_reply_kb())


@dp.callback_query(Build.choosing, F.data.startswith("tpl:"))
async def choose_template(call: CallbackQuery, state: FSMContext):
    key = call.data.split(":", 1)[1]
    if key not in templates.TEMPLATES:
        return await call.answer("قالب پیدا نشد.", show_alert=True)
    await state.update_data(template=key)
    await state.set_state(Build.brand)
    await call.answer()
    await call.message.edit_text(
        f"✅ <b>{html.escape(templates.TEMPLATES[key])}</b>\n\n"
        "1️⃣ نام برند یا نام ربات را بفرست:",
        reply_markup=cancel_reply_kb(),
    )


@dp.message(Build.brand)
async def set_brand(message: Message, state: FSMContext):
    brand = (message.text or "").strip()
    if len(brand) < 2 or len(brand) > 80:
        return await message.answer("⚠️ نام برند باید بین 2 تا 80 کاراکتر باشد.")
    await state.update_data(brand_name=brand)
    await state.set_state(Build.welcome)
    await message.answer("2️⃣ متن خوش‌آمدگویی را بفرست:", reply_markup=cancel_reply_kb())


@dp.message(Build.welcome)
async def set_welcome(message: Message, state: FSMContext):
    welcome = (message.text or "").strip()
    if not welcome:
        return await message.answer("⚠️ متن خوش‌آمدگویی نمی‌تواند خالی باشد.")
    if len(welcome) > 3500:
        return await message.answer("⚠️ متن خوش‌آمدگویی بیش از حد طولانی است. حداکثر 3500 کاراکتر بفرست.")
    if len(welcome) > 3500:
        return await message.answer("⚠️ متن خوش‌آمدگویی بیش از حد طولانی است. حداکثر 3500 کاراکتر بفرست.")
    await state.update_data(welcome_text=welcome)
    await state.set_state(Build.admin)
    await message.answer("3️⃣ آیدی عددی ادمین را بفرست:", reply_markup=cancel_reply_kb())


@dp.message(Build.admin)
async def set_admin(message: Message, state: FSMContext):
    value = (message.text or "").strip()
    if not value.isdigit():
        return await message.answer("⚠️ فقط آیدی عددی معتبر بفرست؛ مثال: 123456789")
    await state.update_data(admin_id=value)
    await state.set_state(Build.detail)
    data = await state.get_data()
    await message.answer(detail_prompt(data["template"]), reply_markup=cancel_reply_kb())


@dp.message(Build.detail)
async def build(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data["template"]
    raw = message.text or ""
    try:
        config = {
            **data,
            **parse_detail(key, raw),
            "contact_info": "برای ارتباط با مدیریت، پیام ارسال کنید.",
        }
        code = templates.build_bot(config)
        compile(code, "<generated_bot.py>", "exec")
    except Exception as exc:
        log.exception("Generation failed")
        return await message.answer(
            "❌ تولید یا اعتبارسنجی کد ناموفق بود.\n"
            f"<code>{html.escape(str(exc))}</code>\n\n"
            "اطلاعات مرحله ۴ را دوباره بفرست.",
            reply_markup=cancel_reply_kb(),
        )

    await state.clear()
    await message.answer(
        "🎉 <b>ربات با موفقیت ساخته شد!</b>\n"
        + SEP
        + f"\nقالب: <b>{html.escape(templates.TEMPLATES[key])}</b>\n\n"
        "📦 فایل <code>bot.py</code> آماده است.\n\n"
        "<b>نصب:</b>\n"
        "<code>pip install aiogram==3.30.0 python-dotenv==1.0.1</code>\n\n"
        "سپس BOT_TOKEN و ADMIN_ID را در محیط تنظیم کن و اجرا کن."
        , reply_markup=home_reply_kb()
    )
    await message.answer_document(
        BufferedInputFile(code.encode("utf-8"), filename=f"{key}_bot.py")
    )


async def main() -> None:
    await bot.set_my_commands([
        BotCommand(command="start", description="🏠 ساخت ربات جدید"),
        BotCommand(command="help", description="ℹ️ راهنما"),
        BotCommand(command="templates", description="✨ مشاهده ۱۰۰ قالب"),
        BotCommand(command="cancel", description="🔴 لغو ساخت"),
    ])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
