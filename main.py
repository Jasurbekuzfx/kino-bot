import logging
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, ADMINS, CHANNELS, INVITE_LINK
import database as db

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    db.add_user(message.from_user.id)
    if await check_sub(message.from_user.id):
        await message.answer(f"🎬 Salom {message.from_user.first_name}!\nKino kodini yuboring:")
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url=INVITE_LINK))
        keyboard.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check"))
        await message.answer("⚠️ Botdan foydalanish uchun kanalimizga a'zo bo'ling:", reply_markup=keyboard)

@dp.callback_query_handler(text="check")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("✅ Rahmat! Kino kodini yuboring:")
    else:
        await call.answer("❌ Hali a'zo bo'lmadingiz!", show_alert=True)

@dp.message_handler(content_types=['video'])
async def save_movie(message: types.Message):
    if message.from_user.id in ADMINS and message.caption and message.caption.startswith("kino:"):
        _, code, title = message.caption.split(":")
        if db.add_movie(code, title, message.video.file_id):
            await message.reply(f"✅ Saqlandi! Kod: {code}")
        else:
            await message.reply("❌ Bu kod band.")

@dp.message_handler(lambda message: message.text.isdigit())
async def search_movie(message: types.Message):
    if not await check_sub(message.from_user.id):
        return await start_cmd(message)
    
    res = db.get_movie(message.text)
    if res:
        await bot.send_video(message.chat.id, res[1], caption=f"🎬 {res[0]}")
    else:
        await message.answer("😔 Kino topilmadi.")

if __name__ == '__main__':
    db.create_db()
    executor.start_polling(dp, skip_updates=True)
