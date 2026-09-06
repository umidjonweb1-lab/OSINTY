from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from database.db import upsert_user, add_name_observation
from keyboards.main import back_menu

router = Router()

@router.message(Command("me"))
async def me(message: Message):
    upsert_user(message.from_user)
    u = message.from_user
    name = " ".join(x for x in [u.first_name, u.last_name] if x)
    add_name_observation(u.id, name or "(no name)")
    await message.answer(
        f"👤 <b>Current account</b>\n\n"
        f"Name: {name or '—'}\nUsername: @{u.username if u.username else '—'}\n"
        f"Telegram ID: <code>{u.id}</code>\n\n"
        "Bu bot ko‘rishi mumkin bo‘lgan account-level/public ma'lumotlar.",
        parse_mode="HTML")

@router.message(Command("profile"))
async def profile(message: Message, bot):
    upsert_user(message.from_user)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        return await message.answer("👤 Misol: <code>/profile @telegram</code>", parse_mode="HTML")
    target = parts[1].strip()
    if not target.startswith("@"):
        target = "@" + target
    try:
        chat = await bot.get_chat(target)
        title = chat.title or " ".join(x for x in [chat.first_name, chat.last_name] if x) or "—"
        username = f"@{chat.username}" if chat.username else "—"
        await message.answer(
            f"👤 <b>Public Telegram entity</b>\n\n"
            f"Name: {title}\nUsername: {username}\n"
            f"ID: <code>{chat.id}</code>\nType: {chat.type}\n\n"
            "Bot API global user-profile database yoki private ma'lumotlarni bermaydi.",
            parse_mode="HTML")
    except Exception:
        await message.answer("❌ Public username/chat topilmadi yoki Bot API orqali ochiq emas.")

@router.callback_query(F.data == "profile")
async def profile_button(call: CallbackQuery):
    await call.message.edit_text(
        "👤 <b>Profile Search</b>\n\n"
        "Public username/chat uchun:\n<code>/profile @username</code>\n\n"
        "O‘zingizni tekshirish:\n<code>/me</code>",
        reply_markup=back_menu(), parse_mode="HTML")
    await call.answer()
