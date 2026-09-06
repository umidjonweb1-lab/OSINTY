from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.db import upsert_user, add_search, add_tracking

router = Router()

def arg(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    return parts[1].strip() if len(parts) == 2 else ""

@router.message(Command("search"))
async def search(message: Message):
    upsert_user(message.from_user)
    q = arg(message)
    if not q:
        return await message.answer("🔎 Misol: <code>/search football</code>", parse_mode="HTML")
    add_search(message.from_user.id, q, "search")
    await message.answer(
        f"🔎 <b>Search</b>\n\nQuery: <code>{q}</code>\n\n"
        "Natija providerga bog‘liq. Telegram Bot API global qidiruv bazasini bermaydi.",
        parse_mode="HTML")

@router.message(Command("human"))
async def human(message: Message):
    upsert_user(message.from_user)
    q = arg(message)
    if not q:
        return await message.answer("👨 Misol: <code>/human John Smith</code>", parse_mode="HTML")
    add_search(message.from_user.id, q, "human")
    await message.answer(
        f"👨 <b>Human Search</b>\n\nQuery: <code>{q}</code>\n\n"
        "Faqat qonuniy/public data source ulanganida real natijalar chiqadi.",
        parse_mode="HTML")

@router.message(Command("text"))
async def text_search(message: Message):
    upsert_user(message.from_user)
    q = arg(message)
    if not q:
        return await message.answer("📝 Misol: <code>/text football</code>", parse_mode="HTML")
    add_search(message.from_user.id, q, "text")
    await message.answer(
        f"📝 <b>Text Search</b>\n\nQuery: <code>{q}</code>\n\n"
        "Natijalar faqat public indeks manbasi orqali beriladi.",
        parse_mode="HTML")

@router.message(Command("track"))
async def track(message: Message):
    upsert_user(message.from_user)
    q = arg(message)
    if not q:
        return await message.answer("🔔 Misol: <code>/track @username</code>", parse_mode="HTML")
    if len(q) > 128:
        return await message.answer("❌ Target juda uzun.")
    add_tracking(message.from_user.id, q)
    await message.answer(
        f"🔔 <b>Tracking added</b>\n\nTarget: <code>{q}</code>\n"
        "O‘zgarishlarni tekshirish uchun public source adapter kerak bo‘ladi.",
        parse_mode="HTML")

@router.message(Command("topchat"))
async def topchat(message: Message):
    await message.answer(
        "🏆 <b>Top Public Chats</b>\n\n"
        "Bu bo‘lim public indeksdan reyting oladi. Hozircha indeks bo‘sh.",
        parse_mode="HTML")
