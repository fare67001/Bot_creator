# -*- coding: utf-8 -*-
"""Bot Factory Pro — 100 production-ready Telegram bot template definitions and generator."""
from __future__ import annotations
import json
import html as _html
from typing import Any


def _q(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False)

# 10 categories × 10 templates = 100.
_RAW = [
    ("🛍 فروش و سفارش", [
        ("shop", "🛍 فروشگاه آنلاین", "catalog_price"),
        ("service_order", "🧾 ثبت سفارش خدمات", "catalog_price"),
        ("restaurant", "🍔 رستوران و سفارش غذا", "catalog_price"),
        ("cafe", "☕ کافه و سفارش منو", "catalog_price"),
        ("bakery", "🥐 نانوایی و سفارش محصولات", "catalog_price"),
        ("flower_shop", "💐 گل‌فروشی", "catalog_price"),
        ("gift_shop", "🎁 فروشگاه هدیه", "catalog_price"),
        ("fashion_shop", "👕 فروشگاه پوشاک", "catalog_price"),
        ("digital_shop", "💻 فروشگاه محصولات دیجیتال", "catalog_price"),
        ("wholesale", "📦 عمده‌فروشی و استعلام قیمت", "catalog_price"),
    ]),
    ("🏢 کسب‌وکار و خدمات", [
        ("agency", "🏢 آژانس خدماتی", "catalog"),
        ("marketing", "📣 آژانس بازاریابی", "catalog"),
        ("design_studio", "🎨 استودیو طراحی", "catalog"),
        ("software_house", "🧑‍💻 شرکت نرم‌افزاری", "catalog"),
        ("consulting", "🧠 مشاوره کسب‌وکار", "booking"),
        ("legal_office", "⚖️ دفتر خدمات حقوقی", "booking"),
        ("accounting", "🧮 خدمات حسابداری", "booking"),
        ("insurance", "🛡️ خدمات بیمه", "booking"),
        ("translation", "🌐 خدمات ترجمه", "form"),
        ("printing", "🖨️ چاپ و خدمات چاپی", "catalog_price"),
    ]),
    ("📅 رزرو و نوبت‌دهی", [
        ("booking", "📅 نوبت‌دهی عمومی", "booking"),
        ("clinic", "🩺 کلینیک و نوبت", "booking"),
        ("dentist", "🦷 دندانپزشکی", "booking"),
        ("beauty_salon", "💇 سالن زیبایی", "booking"),
        ("barbershop", "💈 آرایشگاه مردانه", "booking"),
        ("fitness", "🏋️ باشگاه و مربی", "booking"),
        ("photography", "📸 عکاسی و رزرو جلسه", "booking"),
        ("car_service", "🔧 سرویس خودرو", "booking"),
        ("repair_center", "🛠️ مرکز تعمیرات", "booking"),
        ("pet_clinic", "🐾 کلینیک حیوانات", "booking"),
    ]),
    ("🎓 آموزش و محتوا", [
        ("course", "🎓 فروش دوره آموزشی", "catalog"),
        ("academy", "🏫 آموزشگاه", "catalog"),
        ("ebook", "📚 کتابخانه دیجیتال", "catalog"),
        ("podcast", "🎙️ پادکست و اپیزودها", "content"),
        ("news", "📰 خبرنامه", "content"),
        ("magazine", "🗞️ مجله دیجیتال", "content"),
        ("tutorial", "📘 آموزش و مقالات", "content"),
        ("exam_prep", "📝 آمادگی آزمون", "quiz"),
        ("language_school", "🗣️ آموزش زبان", "catalog"),
        ("webinar", "💻 وبینار و ثبت‌نام", "event"),
    ]),
    ("🎉 رویداد و سرگرمی", [
        ("event", "🎟️ ثبت‌نام رویداد", "event"),
        ("conference", "🏛️ کنفرانس", "event"),
        ("workshop", "🧑‍🏫 کارگاه آموزشی", "event"),
        ("meetup", "🤝 دورهمی و Meetup", "event"),
        ("giveaway", "🎁 قرعه‌کشی", "giveaway"),
        ("contest", "🏆 مسابقه", "quiz"),
        ("quiz", "🎯 آزمون و کوییز", "quiz"),
        ("poll", "📊 نظرسنجی", "poll"),
        ("trivia", "🧩 اطلاعات عمومی", "quiz"),
        ("fan_club", "⭐ باشگاه هواداران", "community"),
    ]),
    ("👥 جامعه و ارتباط", [
        ("support", "🎫 پشتیبانی و تیکت", "support"),
        ("contact", "📞 ارتباط با ما", "contact"),
        ("feedback", "⭐ بازخورد مشتری", "feedback"),
        ("complaint", "⚠️ ثبت شکایت", "form"),
        ("suggestion", "💡 پیشنهادات", "form"),
        ("community", "👥 مدیریت جامعه", "community"),
        ("rules", "📜 قوانین و مقررات", "rules"),
        ("referral", "👥 دعوت دوستان", "referral"),
        ("profile", "👤 پروفایل کاربری", "profile"),
        ("verification", "✅ درخواست احراز هویت", "form"),
    ]),
    ("🏠 املاک و حمل‌ونقل", [
        ("realestate", "🏠 املاک", "catalog_price"),
        ("rental", "🏢 اجاره ملک", "catalog_price"),
        ("roommate", "🛏️ هم‌خانه‌یابی", "catalog"),
        ("jobs", "💼 کاریابی", "catalog"),
        ("classified", "📦 آگهی و بازارچه", "catalog_price"),
        ("car_rental", "🚗 اجاره خودرو", "catalog_price"),
        ("delivery", "🚚 درخواست ارسال", "form"),
        ("courier", "🏍️ پیک و حمل فوری", "form"),
        ("travel", "✈️ خدمات سفر", "catalog"),
        ("hotel", "🏨 رزرو اقامتگاه", "catalog_price"),
    ]),
    ("💎 عضویت و وفاداری", [
        ("membership", "💎 عضویت ویژه", "membership"),
        ("subscription", "🔁 اشتراک دوره‌ای", "membership"),
        ("vip_club", "👑 باشگاه VIP", "membership"),
        ("loyalty", "🎖️ باشگاه مشتریان", "loyalty"),
        ("coupon", "🎟️ کد تخفیف", "coupon"),
        ("rewards", "🏅 امتیازات و پاداش", "loyalty"),
        ("donation", "❤️ جمع‌آوری حمایت", "donation"),
        ("fundraising", "📢 کمپین حمایت", "donation"),
        ("sponsor", "🤝 جذب اسپانسر", "form"),
        ("affiliate", "🔗 همکاری در فروش", "referral"),
    ]),
    ("🔧 ابزارها و فرم‌ها", [
        ("form", "📝 فرم‌ساز", "form"),
        ("survey", "📝 فرم نظرسنجی", "form"),
        ("calculator", "🧮 ماشین‌حساب", "calculator"),
        ("link_hub", "🔗 لینک‌نامه", "links"),
        ("directory", "📇 دایرکتوری کسب‌وکار", "catalog"),
        ("file_store", "📁 مرکز فایل", "file_store"),
        ("menu", "🧭 منوی چندبخشی", "catalog"),
        ("faq", "❓ سوالات متداول", "faq"),
        ("status", "📡 استعلام وضعیت درخواست", "form"),
        ("feedback_form", "📝 فرم دریافت نظر", "feedback"),
    ]),
    ("📢 کانال و انتشار", [
        ("channel", "📢 انتشار در کانال", "channel"),
        ("broadcast", "📣 اطلاع‌رسانی به کاربران", "broadcast"),
        ("newsletter", "✉️ عضویت در خبرنامه", "newsletter"),
        ("announcement", "📢 اعلامیه‌ها", "content"),
        ("release_notes", "🚀 اطلاع‌رسانی نسخه‌ها", "content"),
        ("daily_digest", "☀️ خلاصه روزانه", "content"),
        ("media_hub", "🎬 مرکز رسانه", "content"),
        ("link_catalog", "🔗 کاتالوگ لینک‌ها", "links"),
        ("content_library", "🗂️ آرشیو محتوا", "content"),
        ("admin_publisher", "🛠️ ناشر اختصاصی ادمین", "channel"),
    ]),
]

TEMPLATE_META: dict[str, dict[str, str]] = {}
CATEGORIES: dict[str, list[tuple[str, str]]] = {}
TEMPLATES: dict[str, str] = {}
for category, items in _RAW:
    CATEGORIES[category] = []
    for key, label, kind in items:
        CATEGORIES[category].append((key, label))
        TEMPLATES[key] = label
        TEMPLATE_META[key] = {"category": category, "kind": kind}
assert len(TEMPLATES) == 100, f"Expected 100 templates, got {len(TEMPLATES)}"


def _common(data: dict, label: str, meta: dict[str, str]) -> str:
    brand = data["brand_name"]
    welcome = data["welcome_text"]
    admin = int(data["admin_id"])
    cfg = {**meta, "brand_name": brand, "welcome_text": welcome, "admin_id": admin, "template": label}
    return f'''# -*- coding: utf-8 -*-
"""{brand} — generated by Bot Factory Pro ({label})."""
import asyncio, logging, os, random, html, ast, operator
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "{admin}"))
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN تنظیم نشده است.")
bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
BRAND = {_q(brand)}
WELCOME = {_q(welcome)}
CONFIG = {_q(cfg)}
SEP = "━━━━━━━━━━━━━━━━"

def style_for(text, callback=None):
    lowered = str(text).casefold()
    if callback == "cancel" or any(x in lowered for x in ("لغو", "حذف", "بستن")):
        return "danger"
    if any(x in lowered for x in ("شروع", "ثبت", "ارسال", "تأیید", "عضویت", "رزرو", "سفارش")):
        return "success"
    return "primary"

def kb(rows):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=c, style=style_for(t,c))] for t, c in rows])

def user_label(u):
    return f"{{html.escape(u.full_name)}} (@{{html.escape(u.username or '-')}}) — <code>{{u.id}}</code>"

async def notify(text, *, reply_markup=None):
    try:
        await bot.send_message(ADMIN_ID, text, reply_markup=reply_markup)
    except Exception:
        logging.exception("admin notification failed")

class Flow(StatesGroup):
    input = State()

@dp.message(CommandStart())
async def start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer(f"👋 <b>{{BRAND}}</b>\\n{{SEP}}\\n{{WELCOME}}", reply_markup=home_kb())

@dp.message(Command("help"))
async def help_cmd(m: Message):
    await m.answer("ℹ️ /start منوی اصلی\\n/help راهنما\\n/cancel لغو عملیات")

@dp.message(Command("cancel"))
async def cancel_cmd(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("🔴 عملیات لغو شد.", reply_markup=home_kb())

@dp.callback_query(F.data == "home")
async def home(c: CallbackQuery, state: FSMContext):
    await state.clear(); await c.answer()
    await c.message.answer(f"👋 <b>{{BRAND}}</b>\\n{{SEP}}\\n{{WELCOME}}", reply_markup=home_kb())

@dp.callback_query(F.data == "contact")
async def contact(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flow.input); await state.update_data(flow="contact"); await c.answer()
    await c.message.answer("📞 پیام یا درخواستت را بفرست:")

@dp.message(F.from_user.id == ADMIN_ID, F.reply_to_message)
async def admin_reply(m: Message):
    target = m.reply_to_message
    raw = target.text or target.caption or ""
    marker = "USER_ID="
    if marker not in raw:
        return
    try:
        uid = int(raw.split(marker, 1)[1].split()[0])
        body = m.text or m.caption or "پاسخ ارسال شد."
        await bot.send_message(uid, f"📩 <b>پاسخ مدیریت</b>\\n{{html.escape(body)}}")
        await m.reply("🟢 پاسخ برای کاربر ارسال شد.")
    except Exception:
        await m.reply("❌ ارسال پاسخ ناموفق بود.")

'''


def _home(kind: str) -> str:
    if kind == "catalog_price": return '''return kb([("🛍 مشاهده کاتالوگ", "catalog"), ("📞 تماس با ما", "contact")])'''
    if kind == "catalog": return '''return kb([("📚 مشاهده موارد", "catalog"), ("📞 تماس با ما", "contact")])'''
    if kind == "booking": return '''return kb([("📅 دریافت نوبت", "booking"), ("📞 تماس با ما", "contact")])'''
    if kind == "form": return '''return kb([("📝 شروع فرم", "form"), ("📞 تماس", "contact")])'''
    if kind == "feedback": return '''return kb([("⭐ ثبت بازخورد", "feedback"), ("📞 تماس", "contact")])'''
    if kind == "contact": return '''return kb([("📞 ارسال پیام", "contact")])'''
    if kind == "community": return '''return kb([("📜 قوانین", "rules"), ("👤 پروفایل", "profile"), ("📞 تماس", "contact")])'''
    if kind == "referral": return '''return kb([("👥 لینک دعوت من", "referral"), ("📞 تماس", "contact")])'''
    if kind == "profile": return '''return kb([("👤 پروفایل من", "profile"), ("📞 تماس", "contact")])'''
    if kind == "rules": return '''return kb([("📜 مشاهده قوانین", "rules"), ("🏠 بازگشت", "home")])'''
    if kind == "links": return '''return kb([("🔗 لینک‌ها", "links"), ("🏠 بازگشت", "home")])'''
    if kind == "file_store": return '''return kb([("📁 فایل‌ها", "files"), ("🏠 بازگشت", "home")])'''
    if kind in {"quiz", "poll", "giveaway", "calculator", "membership", "loyalty", "coupon", "donation", "channel", "broadcast", "newsletter", "content"}:
        action = {"quiz":"quiz","poll":"poll","giveaway":"giveaway","calculator":"calculator","membership":"catalog","loyalty":"loyalty","coupon":"coupon","donation":"donation","channel":"publish","broadcast":"broadcast","newsletter":"subscribe","content":"content"}[kind]
        return f'''return kb([("🔵 شروع", "{action}"), ("📞 تماس", "contact")])'''
    return '''return kb([("📞 تماس با ما", "contact")])'''


def _catalog_code(data: dict) -> str:
    items = data.get("items") or data.get("products") or []
    title = data.get("catalog_title") or "📚 فهرست"
    title_escaped = _html.escape(str(title))
    return f'''ITEMS={_q(items)}
@dp.callback_query(F.data=="catalog")
async def catalog(c:CallbackQuery):
    await c.answer()
    if not ITEMS:
        return await c.message.answer("ℹ️ هنوز موردی ثبت نشده است.", reply_markup=kb([("🏠 بازگشت","home")]))
    rows=[]
    for i,x in enumerate(ITEMS[:80]):
        rows.append((f"🔵 {{html.escape(str(x.get('name', x.get('title','مورد'))))}}", f"item:{{i}}"))
    rows.append(("🏠 بازگشت","home"))
    await c.message.answer("{title_escaped}", reply_markup=kb(rows))
@dp.callback_query(F.data.startswith("item:"))
async def item(c:CallbackQuery):
    await c.answer()
    try: x=ITEMS[int(c.data.split(":",1)[1])]
    except Exception: return await c.message.answer("❌ مورد نامعتبر است.")
    name=html.escape(str(x.get('name',x.get('title','مورد')))); desc=html.escape(str(x.get('desc',x.get('text','')))); price=x.get('price','')
    price_line=f"\\n💰 {{html.escape(str(price))}}" if price else ""
    await c.message.answer(f"📌 <b>{{name}}</b>\\n{{SEP}}\\n{{desc}}{{price_line}}", reply_markup=kb([("🟢 درخواست / سفارش","request"),("🏠 بازگشت","home")]))
@dp.callback_query(F.data=="request")
async def request_item(c:CallbackQuery,state:FSMContext):
    await c.answer(); await state.set_state(Flow.input); await state.update_data(flow="request"); await c.message.answer("🟢 اطلاعات لازم برای سفارش/درخواست را بفرست:")
'''


def _generic_flow(kind: str, label: str, prompt: str) -> str:
    return f'''@dp.callback_query(F.data=="{kind}")
async def {kind}_start(c:CallbackQuery,state:FSMContext):
    await c.answer(); await state.set_state(Flow.input); await state.update_data(flow="{kind}")
    await c.message.answer({ _q(prompt) })
'''


def _kind_code(kind: str, data: dict) -> str:
    if kind in {"catalog", "catalog_price", "membership"}:
        return _catalog_code(data)
    if kind == "support":
        return _generic_flow("ticket", "", "🎫 متن تیکت را بفرست؛ پاسخ مدیریت از طریق همین ربات برایت ارسال می‌شود.")
    if kind in {"contact", "form", "feedback", "complaint", "suggestion", "verification", "delivery", "courier", "status", "sponsor", "translation", "repair_center"}:
        prompts={
            "contact":"📞 پیام یا درخواستت را بفرست.", "form":"📝 اطلاعات فرم را ارسال کن.", "feedback":"⭐ نظر و امتیازت را بنویس.",
            "complaint":"⚠️ جزئیات شکایت را بنویس.", "suggestion":"💡 پیشنهادت را بنویس.", "verification":"✅ اطلاعات لازم برای احراز را در یک پیام بفرست.",
            "delivery":"🚚 مبدا، مقصد و توضیحات ارسال را بفرست.", "courier":"🏍️ مبدا، مقصد و جزئیات درخواست را بفرست.",
            "status":"📡 کد یا اطلاعات پیگیری را بفرست.", "sponsor":"🤝 پیشنهاد همکاری و مشخصات تماس را بفرست.",
            "translation":"🌐 متن و مشخصات ترجمه را ارسال کن.", "repair_center":"🛠️ شرح خرابی و اطلاعات تماس را بفرست.",
        }
        return _generic_flow(kind, "", prompts[kind])
    if kind == "booking":
        slots=data.get("slots",[])
        return f'''SLOTS={_q(slots)}
@dp.callback_query(F.data=="booking")
async def booking_start(c:CallbackQuery):
    await c.answer()
    if not SLOTS: return await c.message.answer("ℹ️ هنوز زمان خالی ثبت نشده است.")
    await c.message.answer("📅 زمان موردنظر را انتخاب کن:", reply_markup=kb([(f"🔵 {{html.escape(str(s))}}",f"slot:{{i}}") for i,s in enumerate(SLOTS[:50])]))
@dp.callback_query(F.data.startswith("slot:"))
async def booking_slot(c:CallbackQuery):
    await c.answer("رزرو ثبت شد ✅", show_alert=True)
    idx=int(c.data.split(":",1)[1]); slot=SLOTS[idx]
    await notify(f"📅 <b>رزرو جدید</b>\\n👤 {{user_label(c.from_user)}}\\n🕐 {{html.escape(str(slot))}}\\nUSER_ID={{c.from_user.id}}")
    await c.message.answer("✅ درخواست نوبت ثبت شد.", reply_markup=home_kb())
'''
    if kind == "quiz":
        return f'''QUESTIONS={_q(data.get('questions',[]))}
@dp.callback_query(F.data=="quiz")
async def quiz_start(c:CallbackQuery,state:FSMContext):
    await c.answer(); await state.update_data(score=0); await send_question(c.message,state,0)
async def send_question(m:Message,state:FSMContext,i:int):
    if i>=len(QUESTIONS):
        d=await state.get_data(); score=d.get("score",0); await state.clear()
        return await m.answer(f"🏁 پایان آزمون\\n{{SEP}}\\nامتیاز: <b>{{score}}/{{len(QUESTIONS)}}</b>", reply_markup=home_kb())
    q=QUESTIONS[i]
    await m.answer(f"❓ سوال {{i+1}} از {{len(QUESTIONS)}}\\n{{SEP}}\\n{{html.escape(str(q.get('q','')))}}", reply_markup=kb([(f"🔵 {{html.escape(str(o))}}",f"ans:{{i}}:{{j}}") for j,o in enumerate(q.get('options',[]))]))
@dp.callback_query(F.data.startswith("ans:"))
async def answer(c:CallbackQuery,state:FSMContext):
    _,i,j=c.data.split(":"); i=int(i); j=int(j)
    d=await state.get_data(); correct=int(QUESTIONS[i].get("correct",-1)); score=int(d.get("score",0))+(j==correct)
    await state.update_data(score=score); await c.answer("درست ✅" if j==correct else "اشتباه ❌"); await send_question(c.message,state,i+1)
'''
    if kind == "poll":
        q=data.get("question", "نظرت چیست؟"); opts=data.get("options", [])
        return f'''POLL_Q={_q(q)}; POLL_OPTIONS={_q(opts)}; POLL_VOTES={{}}
@dp.callback_query(F.data=="poll")
async def poll_start(c:CallbackQuery):
    await c.answer(); await c.message.answer(f"📊 <b>{{html.escape(POLL_Q)}}</b>", reply_markup=kb([(f"🔵 {{html.escape(str(o))}}",f"vote:{{i}}") for i,o in enumerate(POLL_OPTIONS)]))
@dp.callback_query(F.data.startswith("vote:"))
async def vote(c:CallbackQuery):
    i=int(c.data.split(":",1)[1]); POLL_VOTES[c.from_user.id]=i; await c.answer("رأی ثبت شد ✅", show_alert=True)
    await c.message.answer("✅ رأی شما ثبت شد.", reply_markup=home_kb())
'''
    if kind == "giveaway":
        return '''PARTICIPANTS=set()
@dp.callback_query(F.data=="giveaway")
async def giveaway(c:CallbackQuery):
    PARTICIPANTS.add(c.from_user.id); await c.answer("ثبت شد 🎁",show_alert=True); await c.message.answer("🎁 شما در قرعه‌کشی ثبت شدید.")
@dp.message(Command("draw"))
async def draw(m:Message):
    if m.from_user.id!=ADMIN_ID: return
    if not PARTICIPANTS: return await m.answer("ℹ️ هنوز شرکت‌کننده‌ای ثبت نشده است.")
    await m.answer(f"🎉 برنده: <code>{{random.choice(list(PARTICIPANTS))}}</code>")
'''
    if kind == "referral":
        return '''@dp.callback_query(F.data=="referral")
async def referral(c:CallbackQuery):
    await c.answer(); me=await bot.get_me(); link=f"https://t.me/{me.username}?start=ref_{c.from_user.id}"; await c.message.answer(f"👥 لینک دعوت شما:\\n<code>{link}</code>")
REFERRALS={}
@dp.message(CommandStart(deep_link=True))
async def referral_start(m:Message, state:FSMContext):
    await state.clear()
    arg=(m.text or "").partition(" " )[2].strip()
    if arg.startswith("ref_"):
        try:
            inviter=int(arg[4:])
            if inviter != m.from_user.id:
                REFERRALS[inviter]=REFERRALS.get(inviter,0)+1
                await bot.send_message(inviter, f"🎉 یک دعوت جدید ثبت شد. مجموع دعوت‌ها: <b>{REFERRALS[inviter]}</b>")
        except ValueError:
            pass
    await m.answer(f"👋 <b>{BRAND}</b>\\n{SEP}\\n{WELCOME}", reply_markup=home_kb())
'''
    if kind == "profile":
        return '''@dp.callback_query(F.data=="profile")
async def profile(c:CallbackQuery):
    await c.answer(); u=c.from_user; await c.message.answer(f"👤 <b>پروفایل</b>\\nنام: {html.escape(u.full_name)}\\nآیدی: <code>{u.id}</code>\\nیوزرنیم: @{html.escape(u.username or '-')}", reply_markup=home_kb())
'''
    if kind == "rules":
        return f'''RULES={_q(data.get('rules',''))}
@dp.callback_query(F.data=="rules")
async def rules(c:CallbackQuery):
    await c.answer(); await c.message.answer(f"📜 <b>قوانین</b>\\n{{SEP}}\\n{{html.escape(RULES) or 'هنوز قانونی ثبت نشده است.'}}", reply_markup=kb([("🏠 بازگشت","home")]))
'''
    if kind == "links":
        links=data.get("links",[])
        return f'''LINKS={_q(links)}
@dp.callback_query(F.data=="links")
async def links(c:CallbackQuery):
    await c.answer(); rows=[]
    for x in LINKS[:40]: rows.append((str(x.get("title","لینک")),str(x.get("url","https://example.com"))))
    await c.message.answer("🔗 لینک‌ها", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t,url=u)] for t,u in rows]))
'''
    if kind == "file_store":
        files=data.get("files",[])
        return f'''FILES={_q(files)}
@dp.callback_query(F.data=="files")
async def files(c:CallbackQuery):
    await c.answer()
    if not FILES: return await c.message.answer("ℹ️ هنوز فایلی ثبت نشده است.")
    for x in FILES[:40]:
        try: await bot.send_document(c.from_user.id,x.get("file_id"),caption=html.escape(str(x.get("title","فایل"))))
        except Exception: pass
'''
    if kind == "calculator":
        return '''@dp.callback_query(F.data=="calculator")
async def calculator(c:CallbackQuery,state:FSMContext):
    await c.answer(); await state.set_state(Flow.input); await state.update_data(flow="calculator"); await c.message.answer("🧮 یک عبارت مثل 12*7+5 بفرست.")
OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Mod:operator.mod,ast.Pow:operator.pow}
def safe_eval(expr):
    def ev(n):
        if isinstance(n,ast.Expression): return ev(n.body)
        if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)): return n.value
        if isinstance(n,ast.BinOp) and type(n.op) in OPS: return OPS[type(n.op)](ev(n.left),ev(n.right))
        if isinstance(n,ast.UnaryOp) and isinstance(n.op,(ast.USub,ast.UAdd)): return -ev(n.operand) if isinstance(n.op,ast.USub) else ev(n.operand)
        raise ValueError
    return ev(ast.parse(expr,mode="eval"))
'''
    if kind == "loyalty":
        return '''POINTS={}
@dp.callback_query(F.data=="loyalty")
async def loyalty(c:CallbackQuery):
    await c.answer(); p=POINTS.get(c.from_user.id,0); await c.message.answer(f"🏅 امتیاز فعلی شما: <b>{p}</b>", reply_markup=home_kb())
@dp.message(Command("addpoints"))
async def addpoints(m:Message):
    if m.from_user.id!=ADMIN_ID: return
    parts=(m.text or "").split()
    if len(parts)!=3 or not parts[1].isdigit() or not parts[2].lstrip("-").isdigit():
        return await m.answer("فرمت: /addpoints USER_ID POINTS")
    uid=int(parts[1]); points=int(parts[2]); POINTS[uid]=int(POINTS.get(uid,0))+points; await m.answer(f"✅ امتیاز کاربر: {POINTS[uid]}")
'''
    if kind == "coupon":
        return f'''COUPONS={_q(data.get('coupons',[]))}
@dp.callback_query(F.data=="coupon")
async def coupon(c:CallbackQuery,state:FSMContext):
    await c.answer(); await state.set_state(Flow.input); await state.update_data(flow="coupon"); await c.message.answer("🎟️ کد تخفیف را بفرست.")
'''
    if kind == "donation":
        return _generic_flow("donation", "", "❤️ مبلغ و توضیح حمایتت را بفرست تا برای مدیریت ارسال شود.")
    if kind == "channel":
        return f'''CHANNEL={_q(data.get('channel','@yourchannel'))}
@dp.callback_query(F.data=="publish")
async def publish_hint(c:CallbackQuery): await c.answer(); await c.message.answer("📢 هر پیام متنی، عکس، ویدیو یا فایل را برای من بفرست؛ ادمین می‌تواند آن را منتشر کند.")
@dp.message(F.from_user.id==ADMIN_ID)
async def publish(m:Message):
    if m.text and m.text.startswith('/'): return
    try: await bot.copy_message(CHANNEL,m.chat.id,m.message_id); await m.answer("📢 منتشر شد ✅")
    except Exception as e: await m.answer(f"❌ {{html.escape(str(e))}}")
'''
    if kind == "broadcast":
        return '''@dp.callback_query(F.data=="broadcast")
async def broadcast_info(c:CallbackQuery): await c.answer(); await c.message.answer("📣 این قالب برای اطلاع‌رسانی مدیریت طراحی شده است. لیست مخاطبان در حافظه نگهداری می‌شود.")
AUDIENCE=set()
@dp.message()
async def collect_users(m:Message):
    if m.from_user.id!=ADMIN_ID: AUDIENCE.add(m.from_user.id); return
'''
    if kind == "newsletter":
        return '''SUBSCRIBERS=set()
@dp.callback_query(F.data=="subscribe")
async def subscribe(c:CallbackQuery): SUBSCRIBERS.add(c.from_user.id); await c.answer("عضویت انجام شد ✅",show_alert=True); await c.message.answer("✅ عضو خبرنامه شدی.")
@dp.message(Command("send_news"))
async def send_news(m:Message):
    if m.from_user.id!=ADMIN_ID: return
    body=m.text.partition(" ")[2].strip()
    if not body: return await m.answer("فرمت: /send_news متن خبر")
    sent=0
    for uid in list(SUBSCRIBERS):
        try: await bot.send_message(uid,body); sent+=1
        except Exception: pass
    await m.answer(f"📬 ارسال شد: {sent}")
'''
    if kind == "faq":
        items=data.get("items",[])
        return f'''FAQ={_q(items)}
@dp.callback_query(F.data=="faq")
async def faq(c:CallbackQuery):
    await c.answer()
    if not FAQ: return await c.message.answer("ℹ️ هنوز سوالی ثبت نشده است.")
    text="\\n\\n".join(f"❓ <b>{{html.escape(str(x.get('q','')))}}</b>\\n{{html.escape(str(x.get('a','')))}}" for x in FAQ[:50])
    await c.message.answer(text,reply_markup=kb([("🏠 بازگشت","home")]))
'''
    if kind == "content":
        items=data.get("items",[])
        return f'''CONTENT={_q(items)}
@dp.callback_query(F.data=="content")
async def content(c:CallbackQuery):
    await c.answer(); rows=[(f"📰 {{html.escape(str(x.get('title','مطلب')))}}",f"content:{{i}}") for i,x in enumerate(CONTENT[:60])]
    await c.message.answer("📰 محتوا",reply_markup=kb(rows or [("🏠 بازگشت","home")]))
@dp.callback_query(F.data.startswith("content:"))
async def content_item(c:CallbackQuery):
    await c.answer(); x=CONTENT[int(c.data.split(":",1)[1])]; await c.message.answer(f"📰 <b>{{html.escape(str(x.get('title','مطلب')))}}</b>\\n{{SEP}}\\n{{html.escape(str(x.get('text',x.get('desc',''))))}}")
'''
    if kind == "event":
        return _catalog_code({**data, "catalog_title":"🎟 رویدادها"}) + _generic_flow("event_register", "", "🎟️ نام و شماره تماس و رویداد مدنظر را بفرست.")
    if kind == "community":
        return _kind_code("rules", data) + _kind_code("profile", data)
    return ""


def _detail_help(meta: dict[str, str], data: dict) -> str:
    kind=meta["kind"]
    if kind in {"catalog", "catalog_price", "membership"}:
        return "هر مورد در یک خط: عنوان | توضیح" if kind=="catalog" else "هر مورد در یک خط: عنوان | قیمت | توضیح"
    if kind=="booking": return "هر زمان در یک خط؛ مثال: شنبه 18:00"
    if kind=="quiz": return "هر سوال: سوال | گزینه۱,گزینه۲,گزینه۳ | شماره گزینه صحیح"
    if kind=="poll": return "فرمت: سوال | گزینه۱,گزینه۲,گزینه۳"
    if kind=="links": return "هر لینک: عنوان | https://example.com"
    if kind=="file_store": return "هر فایل: عنوان | file_id تلگرام"
    if kind=="channel": return "یوزرنیم کانال مثل @mychannel"
    if kind=="rules": return "متن کامل قوانین"
    if kind in {"form","feedback","complaint","suggestion","verification"}: return "نام فیلدها را با کاما جدا کن؛ مثال: نام, شماره تماس, توضیحات"
    if kind=="content": return "هر محتوا: عنوان | متن"
    if kind=="event": return "هر رویداد: عنوان | توضیح"
    return "/empty"


def build_bot(data: dict) -> str:
    template=data["template"]
    label=TEMPLATES[template]
    meta=TEMPLATE_META[template]
    code=_common(data,label,meta)
    # Home keyboard is injected as a closed-over configuration function.
    code += "def home_kb():\n    " + _home(meta["kind"]).replace("return ", "return ", 1) + "\n\n"
    code += _kind_code(meta["kind"], data)
    if meta["kind"] in {"catalog", "catalog_price", "membership", "form", "feedback", "contact", "support", "donation", "coupon", "translation", "delivery", "courier", "status", "sponsor", "verification", "repair_center", "event"}:
        code += '''\n@dp.message(Flow.input)\nasync def flow_input(m:Message,state:FSMContext):\n    d=await state.get_data(); flow=d.get("flow"); text=m.text or m.caption or "پیام رسانه‌ای"\n    await state.clear()\n    if flow=="calculator": return\n    if flow=="coupon":\n        await m.answer("ℹ️ کد دریافت شد و برای مدیریت ثبت شد.",reply_markup=home_kb())\n    elif flow=="request":\n        await notify(f"🧾 <b>درخواست جدید</b>\\n👤 {{user_label(m.from_user)}}\\nUSER_ID={{m.from_user.id}}\\n\\n{{html.escape(text)}}")\n        await m.answer("✅ درخواست ثبت شد.",reply_markup=home_kb())\n    else:\n        await notify(f"📨 <b>{{html.escape(str(flow or 'درخواست'))}}</b>\\n👤 {{user_label(m.from_user)}}\\nUSER_ID={{m.from_user.id}}\\n\\n{{html.escape(text)}}")\n        await m.answer("✅ پیام شما ثبت و برای مدیریت ارسال شد.",reply_markup=home_kb())\n'''
    if meta["kind"] == "calculator":
        code += '''\n@dp.message(Flow.input)\nasync def calculator_input(m:Message,state:FSMContext):\n    d=await state.get_data()\n    if d.get("flow")!="calculator": return\n    expr=(m.text or "").strip(); await state.clear()\n    if len(expr)>80: return await m.answer("⚠️ عبارت خیلی طولانی است.")\n    try: result=safe_eval(expr)\n    except Exception: return await m.answer("❌ عبارت نامعتبر است.",reply_markup=home_kb())\n    await m.answer(f"🧮 نتیجه: <b>{{result}}</b>",reply_markup=home_kb())\n'''
    code += '''\nasync def main():\n    await bot.set_my_commands([BotCommand(command="start",description="🏠 شروع"),BotCommand(command="help",description="ℹ️ راهنما"),BotCommand(command="cancel",description="🔴 لغو")])\n    await dp.start_polling(bot)\nif __name__=="__main__": asyncio.run(main())\n'''
    return code


def detail_prompt(template: str) -> str:
    meta=TEMPLATE_META[template]
    return "4️⃣ اطلاعات اختصاصی قالب را بفرست:\n\n" + _detail_help(meta, {})
