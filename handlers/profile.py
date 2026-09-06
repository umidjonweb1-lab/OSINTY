from html import escape
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from database.db import (
    upsert_user, add_name_observation, get_local_user, get_name_history,
    user_search_count,
)
from keyboards.main import back_menu

router = Router()


def profile_keyboard(telegram_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💠 Name History", callback_data=f"names:{telegram_id}")],
        [InlineKeyboardButton(text="🔎 Search again", callback_data="search")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu")],
    ])


def name_of(user):
    return " ".join(x for x in [user.first_name, user.last_name] if x) or "—"


def render_local_profile(row, source="Local index"):
    name = " ".join(x for x in [row["first_name"], row["last_name"]] if x) or "—"
    username = f'@{row["username"]}' if row["username"] else "—"
    return (
        "👤 <b>PROFILE</b>\n\n"
        f"Name: <b>{escape(name)}</b>\n"
        f"Username: {escape(username)}\n"
        f"Telegram ID: <code>{row['telegram_id']}</code>\n"
        f"Type: {'Bot' if row['is_bot'] else 'User'}\n"
        f"Last activity in bot: {row['last_activity']}\n"
        f"Search records: {user_search_count(row['telegram_id'])}\n"
        f"Source: {escape(source)}\n\n"
        "⚠️ Private chats, contacts, login codes and hidden data are not shown."
    )


@router.message(Command("me"))
async def me(message: Message):
    upsert_user(message.from_user)
    u = message.from_user
    display = name_of(u)
    add_name_observation(u.id, display, u.username)
    row = get_local_user(u.id)
    await message.answer(render_local_profile(row, "Bot interaction"), parse_mode="HTML", reply_markup=profile_keyboard(u.id))


@router.message(Command("profile"))
async def profile(message: Message, bot):
    upsert_user(message.from_user)
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2:
        return await message.answer(
            "👤 <b>Profile Search</b>\n\n"
            "<code>/profile @username</code> — public username\n"
            "<code>/profile 123456789</code> — local indexed ID",
            parse_mode="HTML")

    target = parts[1].strip()
    if target.isdigit() or (target.startswith("-") and target[1:].isdigit()):
        row = get_local_user(int(target))
        if row:
            return await message.answer(render_local_profile(row), parse_mode="HTML", reply_markup=profile_keyboard(row["telegram_id"]))
        return await message.answer(
            "❌ Profil topilmadi. Username orqali qayta urinib ko‘ring yoki foydalanuvchi bot bilan muloqot qilgan bo‘lsa ID ni kiriting.",
            parse_mode="HTML", reply_markup=back_menu())

    username = target if target.startswith("@") else "@" + target
    try:
        chat = await bot.get_chat(username)
        title = chat.title or " ".join(x for x in [chat.first_name, chat.last_name] if x) or "—"
        uname = f"@{chat.username}" if chat.username else "—"
        text = (
            "👤 <b>PUBLIC TELEGRAM ENTITY</b>\n\n"
            f"Name: <b>{escape(title)}</b>\n"
            f"Username: {escape(uname)}\n"
            f"ID: <code>{chat.id}</code>\n"
            f"Type: {chat.type}\n"
        )
        if chat.type in {"group", "supergroup", "channel"}:
            try:
                count = await bot.get_chat_member_count(chat.id)
                text += f"Members/Subscribers: <b>{count}</b>\n"
            except Exception:
                pass
        text += "\nSource: Telegram Bot API public entity lookup."
        return await message.answer(text, parse_mode="HTML", reply_markup=back_menu())
    except Exception:
        await message.answer(
            "❌ Username yoki public chat topilmadi.\n\n"
            "Username ni tekshirib qayta urinib ko‘ring.",
            parse_mode="HTML", reply_markup=back_menu())


@router.callback_query(F.data.startswith("names:"))
async def names_history(call: CallbackQuery):
    try:
        telegram_id = int(call.data.split(":", 1)[1])
    except (ValueError, IndexError):
        return await call.answer("ID xato", show_alert=True)
    rows = get_name_history(telegram_id, 10)
    if not rows:
        text = "💠 <b>Name History</b>\n\nTarix hali yig‘ilmagan."
    else:
        lines = ["💠 <b>Name History</b>", ""]
        for i, row in enumerate(rows, 1):
            uname = f" — @{row['username']}" if row['username'] else ""
            lines.append(f"{i}. {escape(row['display_name'])}{escape(uname)}\n   <i>{row['observed_at']}</i>")
        text = "\n".join(lines)
    await call.message.edit_text(text, parse_mode="HTML", reply_markup=profile_keyboard(telegram_id))
    await call.answer()


@router.callback_query(F.data == "profile")
async def profile_button(call: CallbackQuery):
    await call.message.edit_text(
        "👤 <b>Profile Search</b>\n\n"
        "<code>/profile @username</code> — public entity\n"
        "<code>/profile 123456789</code> — local indexed ID\n\n"
        "O‘zingizni tekshirish: <code>/me</code>",
        reply_markup=back_menu(), parse_mode="HTML")
    await call.answer()
