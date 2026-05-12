import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import TOKEN, ADMINS, CHANNELS, INVITE_LINK
import database as db

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Kanallarga a'zolikni tekshirish
async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    db.add_user(message.from_user.id) # Foydalanuvchini bazaga qo'shish
    if await check_sub(message.from_user.id):
        await message.answer(f"🎬 Salom {message.from_user.first_name}!\nKino kodini yuboring:")
    else:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=INVITE_LINK))
        builder.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check"))
        await message.answer("⚠️ Botdan foydalanish uchun kanalimizga a'zo bo'ling:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "check")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("✅ Rahmat! Kino kodini yuboring:")
    else:
        await call.answer("❌ Hali a'zo bo'lmadingiz!", show_alert=True)

# Admin uchun statistika
@dp.message(Command("stat"), F.from_user.id.in_(ADMINS))
async def stat_cmd(message: types.Message):
    count = db.count_users()
    await message.answer(f"📊 Bot foydalanuvchilari soni: {count} ta")

# Admin uchun kino qo'shish (Video yuborib captionga 'kino:kod:nomi' yoziladi)
@dp.message(F.video, F.from_user.id.in_(ADMINS))
async def save_movie_handler(message: types.Message):
    if message.caption and message.caption.startswith("kino:"):
        _, code, title = message.caption.split(":")
        if db.add_movie(code, title, message.video.file_id):
            await message.reply(f"✅ Saqlandi!\nKod: {code}\nNomi: {title}")
        else:
            await message.reply("❌ Bu kod band.")

# Kino qidirish
@dp.message(F.text.isdigit())
async def search_handler(message: types.Message):
    if not await check_sub(message.from_user.id):
        return await start_cmd(message)
    
    res = db.get_movie(message.text)
    if res:
        title, file_id = res
        await bot.send_video(chat_id=message.chat.id, video=file_id, caption=f"🎬 {title}\n🆔 Kod: {message.text}")
    else:
        await message.answer("😔 Kino topilmadi.")

async def main():
    db.create_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
