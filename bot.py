import asyncio, os, re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus

dp = Dispatcher()
COMMANDS = {"سنجاق", "باز کن", "حذف پیام", "اخراج", "رفع سکوت", "راهنما"}

def normalize(s):
    return " ".join(s.translate(str.maketrans({"ي":"ی","ك":"ک","\u200c":" "})).split())

async def admin(bot, chat, uid):
    member = await bot.get_chat_member(chat, uid)
    return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)

@dp.message(F.text)
async def handle(m: Message):
    if m.chat.type not in ("group", "supergroup") or not m.from_user:
        return
    cmd = normalize(m.text)
    if cmd not in COMMANDS:
        return
    if cmd == "راهنما":
        await m.reply("سنجاق | باز کن | حذف پیام | اخراج | رفع سکوت")
        return
    if not await admin(m.bot, m.chat.id, m.from_user.id):
        return
    target = m.reply_to_message
    if not target:
        await m.reply("روی پیام موردنظر ریپلای کن.")
        return
    try:
        if cmd == "سنجاق":
            await m.bot.pin_chat_message(m.chat.id, target.message_id)
        elif cmd == "باز کن":
            await m.bot.unpin_chat_message(m.chat.id, target.message_id)
        elif cmd == "حذف پیام":
            await target.delete()
        else:
            if not target.from_user or target.sender_chat:
                return
            uid = target.from_user.id
            if await admin(m.bot, m.chat.id, uid):
                return
            if cmd == "اخراج":
                await m.bot.ban_chat_member(m.chat.id, uid)
                await m.bot.unban_chat_member(m.chat.id, uid, only_if_banned=True)
            elif cmd == "رفع سکوت":
                from aiogram.types import ChatPermissions
                await m.bot.restrict_chat_member(m.chat.id, uid, ChatPermissions(
                    can_send_messages=True, can_send_other_messages=True,
                    can_send_media_messages=True, can_send_polls=True))
        await m.reply("عملیات انجام شد.")
    except Exception:
        await m.reply("عملیات انجام نشد؛ دسترسی ربات و نوع گروه را بررسی کن.")

async def main():
    bot = Bot(os.environ["BOT_TOKEN"])
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
