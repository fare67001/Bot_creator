# -*- coding: utf-8 -*-
"""Bot Factory Pro v11 — professional Telegram bot builder with 100 domain profiles."""
from __future__ import annotations
import asyncio, html, logging, os
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BufferedInputFile, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardMarkup
from dotenv import load_dotenv
import templates

load_dotenv()
BOT_TOKEN=os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise SystemExit('BOT_TOKEN تنظیم نشده است.')
logging.basicConfig(level=logging.INFO)
log=logging.getLogger('bot_factory')
bot=Bot(BOT_TOKEN,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp=Dispatcher(storage=MemoryStorage())
SEP='━━━━━━━━━━━━━━━━'

class Build(StatesGroup):
    choosing=State(); brand=State(); welcome=State(); admin=State(); detail=State()


def style_for(text: str, callback: str|None=None) -> str:
    t=text.casefold()
    if callback and (callback.startswith('cancel') or any(x in t for x in ('لغو','حذف','رد','خروج'))): return 'danger'
    if any(x in t for x in ('ساخت','شروع','تأیید','ثبت','افزودن','سفارش','رزرو','آموزش')): return 'success'
    return 'primary'


def ikb(rows:list[tuple[str,str]], cols:int=2):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t,callback_data=c,style=style_for(t,c)) for t,c in rows[i:i+cols]] for i in range(0,len(rows),cols)])


def rkb(rows:list[list[str]]):
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=x,style=style_for(x)) for x in row] for row in rows],resize_keyboard=True,is_persistent=True,input_field_placeholder='انتخاب کنید…')


def home_text():
    return f"🤖 <b>BOT FACTORY PRO v10</b>\n<i>کارخانه ساخت ربات‌های حرفه‌ای تلگرام</i>\n{SEP}\n🚀 <b>100 قالب تخصصی</b> | ⚡ تولید سریع | 🧩 هسته تجاری\n\nیک قالب را انتخاب کن و ربات مستقل خودت را بساز."


def home_reply():
    return rkb([["🚀 ساخت ربات جدید","✨ مشاهده ۱۰۰ قالب"],["📊 آمار کارخانه","🎓 آموزش راه‌اندازی"]])


def cancel_reply():
    return rkb([["🔴 لغو ساخت","🎓 آموزش راه‌اندازی"],["🏠 خانه"]])


def cats_reply():
    labels=list(templates.CATEGORIES)
    return rkb([labels[i:i+2] for i in range(0,len(labels),2)]+[["✨ نمایش همه ۱۰۰ قالب","🎓 آموزش راه‌اندازی"],["🏠 خانه"]])


def all_reply(page:int=0):
    items=list(templates.TEMPLATES.items()); size=20; pages=(len(items)+size-1)//size; page=max(0,min(page,pages-1))
    labels=[x[1] for x in items[page*size:(page+1)*size]]; rows=[labels[i:i+2] for i in range(0,len(labels),2)]
    nav=[]
    if page>0: nav.append('⬅️ قبلی')
    if page<pages-1: nav.append('بعدی ➡️')
    if nav: rows.append(nav)
    rows += [['🔙 دسته‌ها','🎓 آموزش راه‌اندازی'],['🏠 خانه']]
    return rkb(rows)


def category_reply(index:int):
    name=list(templates.CATEGORIES)[index]; labels=[label for _,label in templates.CATEGORIES[name]]
    rows=[labels[i:i+2] for i in range(0,len(labels),2)]; rows += [['🔙 دسته‌ها','🎓 آموزش راه‌اندازی'],['🏠 خانه']]
    return rkb(rows)


def inline_home():
    return ikb([('🚀 ساخت ربات جدید','cats'),('✨ مشاهده ۱۰۰ قالب','all:0'),('📊 آمار کارخانه','stats'),('🎓 آموزش راه‌اندازی','guide')],2)


def full_guide_text():
    return ("🎓 <b>آموزش کامل ساخت و راه‌اندازی ربات</b>\n"+SEP+"\n"
    "<b>1️⃣ ساخت</b>\nقالب را انتخاب کن، اطلاعات برند و تنظیماتش را کامل کن و فایل ربات را دریافت کن.\n\n"
    "<b>2️⃣ GitHub</b>\nیک Repository جدید بساز و <code>bot.py</code> و <code>requirements.txt</code> را مستقیم در ریشه Commit کن. Token و <code>.env</code> را هرگز Commit نکن.\n\n"
    "<b>3️⃣ Railway</b>\nNew Project → Deploy from GitHub Repo → Repository ربات را انتخاب کن.\n\n"
    "<b>4️⃣ Variables</b>\n<code>BOT_TOKEN</code> اجباری است. قالب‌های دارای مدیریت/سفارش به <code>ADMIN_ID</code> نیاز دارند؛ کانال به <code>CHANNEL</code> و پرداخت خارجی اختیاری به <code>PAYMENT_URL</code>.\n\n"
    "<b>5️⃣ Start Command</b>\nاگر خودکار پیدا نشد: <code>python bot.py</code>\n\n"
    "<b>6️⃣ دیتابیس</b>\nبرای هر ربات یک PostgreSQL در Railway اضافه کن و <code>DATABASE_URL</code> را به سرویس ربات متصل کن. اطلاعات در PostgreSQL باقی می‌ماند.\n\n"
    "<b>7️⃣ تست نهایی</b>\nTelegram → /start → منوی اصلی → قابلیت تخصصی قالب → لغو عملیات → سناریوی ادمین.\n\n"
    "🔐 Token فقط در Railway Variables.\n✅ GitHub → Railway → Variables → Start Command → Deploy → Logs → /start")


@dp.message(CommandStart())
async def start(m:Message,state:FSMContext):
    await state.clear(); await state.update_data(all_page=0)
    await m.answer(home_text(),reply_markup=home_reply())
    await m.answer('👇 <b>منوی سریع</b>',reply_markup=inline_home())

@dp.message(F.text=='🎓 آموزش راه‌اندازی')
async def guide_reply(m:Message): await m.answer(full_guide_text(),reply_markup=home_reply())

@dp.callback_query(F.data=='guide')
async def guide_cb(c:CallbackQuery): await c.answer(); await c.message.answer(full_guide_text(),reply_markup=home_reply())

@dp.message(Command('help'))
async def help_cmd(m:Message): await m.answer(full_guide_text(),reply_markup=home_reply())

@dp.message(Command('cancel'))
async def cancel_cmd(m:Message,state:FSMContext): await state.clear(); await m.answer('🔴 ساخت لغو شد.',reply_markup=home_reply())

@dp.callback_query(F.data=='cancel')
async def cancel_cb(c:CallbackQuery,state:FSMContext): await state.clear(); await c.answer('لغو شد',show_alert=True); await c.message.answer('🔴 ساخت لغو شد.',reply_markup=home_reply())

@dp.callback_query(F.data=='cats')
async def cats(c:CallbackQuery,state:FSMContext): await state.set_state(Build.choosing); await c.answer(); await c.message.answer('📚 <b>دسته‌بندی‌ها</b>',reply_markup=cats_reply())

@dp.callback_query(F.data.startswith('cat:'))
async def cat(c:CallbackQuery,state:FSMContext):
    idx=int(c.data.split(':',1)[1]); names=list(templates.CATEGORIES)
    if not 0<=idx<len(names): return await c.answer('دسته نامعتبر',show_alert=True)
    await state.set_state(Build.choosing); await state.update_data(category_index=idx); await c.answer(); await c.message.answer(f'✨ <b>{html.escape(names[idx])}</b>',reply_markup=category_reply(idx))

@dp.callback_query(F.data.startswith('all:'))
async def all_cb(c:CallbackQuery,state:FSMContext):
    page=int(c.data.split(':',1)[1]); pages=(len(templates.TEMPLATES)+19)//20; page=max(0,min(page,pages-1))
    await state.set_state(Build.choosing); await state.update_data(all_page=page); await c.answer(); await c.message.answer(f'✨ <b>همه ۱۰۰ قالب</b> — صفحه {page+1}/{pages}',reply_markup=all_reply(page))


def label_to_key(text:str): return next((k for k,v in templates.TEMPLATES.items() if v==text),None)


async def home_for(message:Message,state:FSMContext):
    await state.clear(); await message.answer(home_text(),reply_markup=home_reply()); await message.answer('👇 <b>منوی سریع</b>',reply_markup=inline_home())

@dp.message(Build.choosing)
async def choose_text(m:Message,state:FSMContext):
    text=(m.text or '').strip(); names=list(templates.CATEGORIES)
    if text=='🏠 خانه': return await home_for(m,state)
    if text=='🔴 لغو ساخت': await state.clear(); return await m.answer('🔴 لغو شد.',reply_markup=home_reply())
    if text=='🎓 آموزش راه‌اندازی': return await m.answer(full_guide_text(),reply_markup=home_reply())
    if text=='🚀 ساخت ربات جدید': return await m.answer('📚 دسته را انتخاب کن:',reply_markup=cats_reply())
    if text in ('✨ مشاهده ۱۰۰ قالب','✨ نمایش همه ۱۰۰ قالب'):
        await state.update_data(all_page=0); return await m.answer('✨ صفحه 1/5',reply_markup=all_reply(0))
    if text in names:
        idx=names.index(text); await state.update_data(category_index=idx); return await m.answer(f'✨ <b>{html.escape(text)}</b>',reply_markup=category_reply(idx))
    if text=='🔙 دسته‌ها': return await m.answer('📚 دسته‌ها',reply_markup=cats_reply())
    if text in ('⬅️ قبلی','بعدی ➡️'):
        d=await state.get_data(); p=int(d.get('all_page',0)); p=max(0,p-1) if 'قبلی' in text else min(4,p+1)
        await state.update_data(all_page=p); return await m.answer(f'✨ صفحه {p+1}/5',reply_markup=all_reply(p))
    key=label_to_key(text)
    if key:
        await state.update_data(template=key); await state.set_state(Build.brand); return await m.answer('1️⃣ نام برند یا ربات را بفرست:',reply_markup=cancel_reply())
    await m.answer('⚠️ از دکمه‌های منو استفاده کن.',reply_markup=home_reply())

@dp.callback_query(Build.choosing,F.data.startswith('tpl:'))
async def tpl(c:CallbackQuery,state:FSMContext):
    key=c.data.split(':',1)[1]
    if key not in templates.TEMPLATES: return await c.answer('قالب پیدا نشد',show_alert=True)
    await state.update_data(template=key); await state.set_state(Build.brand); await c.answer(); await c.message.answer(f'✅ <b>{html.escape(templates.TEMPLATES[key])}</b>\n\n1️⃣ نام برند یا ربات را بفرست:',reply_markup=cancel_reply())

@dp.message(Build.brand)
async def brand(m:Message,state:FSMContext):
    v=(m.text or '').strip()
    if not 2<=len(v)<=80: return await m.answer('⚠️ نام برند باید 2 تا 80 کاراکتر باشد.')
    await state.update_data(brand_name=v); await state.set_state(Build.welcome); await m.answer('2️⃣ متن خوش‌آمدگویی را بفرست:',reply_markup=cancel_reply())

@dp.message(Build.welcome)
async def welcome(m:Message,state:FSMContext):
    v=(m.text or '').strip()
    if not v or len(v)>3500: return await m.answer('⚠️ متن خوش‌آمدگویی باید 1 تا 3500 کاراکتر باشد.')
    await state.update_data(welcome_text=v); await state.set_state(Build.admin); await m.answer('3️⃣ آیدی عددی ادمین را بفرست:',reply_markup=cancel_reply())

@dp.message(Build.admin)
async def admin(m:Message,state:FSMContext):
    v=(m.text or '').strip()
    if not v.isdigit(): return await m.answer('⚠️ فقط آیدی عددی معتبر بفرست؛ مثال 123456789')
    await state.update_data(admin_id=v); await state.set_state(Build.detail)
    d=await state.get_data(); await m.answer(templates.detail_prompt(d['template']),reply_markup=cancel_reply())

@dp.message(Build.detail)
async def detail(m:Message,state:FSMContext):
    d=await state.get_data(); d['detail']=(m.text or '').strip()
    try:
        code=templates.build_bot(d); compile(code,'<generated_bot.py>','exec')
    except Exception as exc:
        log.exception('generation failed'); return await m.answer('❌ تولید ناموفق بود.\n'+f'<code>{html.escape(str(exc))}</code>\n\nمرحله 4 را دوباره بفرست.',reply_markup=cancel_reply())
    await state.clear()
    await m.answer('🎉 <b>ربات تجاری آماده شد!</b>\n'+SEP+'\n✅ PostgreSQL ماندگار\n✅ پنل ادمین + 💾 دریافت دیتابیس\n✅ ثبت اطلاعات کاربران و تعاملات\n✅ ماژول‌های تخصصی قالب\n✅ لغو امن عملیات/سفارش\n✅ Referral / Loyalty / Coupon در قالب‌های مربوط\n✅ GitHub + Railway Ready\n\n📦 یک بسته کامل شامل bot.py، requirements.txt، .env.example و README تحویل می‌گیری.\n\n<code>BOT_TOKEN=...</code>\n<code>ADMIN_ID=...</code>\n<code>DATABASE_URL=...</code>',reply_markup=home_reply())
    package=templates.build_package(d)
    await m.answer_document(BufferedInputFile(package,filename=f"{d['template']}_bot_railway.zip"))
    await m.answer_document(BufferedInputFile(code.encode('utf-8'),filename=f"{d['template']}_bot.py"))

@dp.message(F.text=='📊 آمار کارخانه')
async def stats(m:Message):
    kinds={meta['engine'] for meta in templates.TEMPLATE_META.values()}
    await m.answer(f'📊 <b>Bot Factory Pro v11</b>\n{SEP}\n🧩 قالب‌ها: <b>{len(templates.TEMPLATES)}</b>\n📚 دسته‌ها: <b>{len(templates.CATEGORIES)}</b>\n🧠 پروفایل‌های تخصصی: <b>{len(kinds)}</b>\n🏗️ هسته: Commercial Core\n🧪 تست: 100 generator paths + compile',reply_markup=home_reply())

async def main():
    await bot.set_my_commands([BotCommand(command='start',description='🏠 شروع'),BotCommand(command='help',description='🎓 راهنما'),BotCommand(command='cancel',description='🔴 لغو')])
    await dp.start_polling(bot)

if __name__=='__main__': asyncio.run(main())
