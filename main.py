import logging
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, ADMINS, CHANNELS
from database import Database # Bazangiz nomi qanday bo'lsa shunday qoldiring

# Botni sozlash
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
db = Database('kino_bot.db')

# 1. Obunani tekshirish funksiyasi
async def check_sub(user_id):
    for channel_id in CHANNELS.keys():
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

# 2. Start komandasi
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    db.add_user(message.from_user.id) 

    if await check_sub(message.from_user.id):
        await message.answer(f"🎬 Salom {message.from_user.first_name}!\nKino kodini yuboring:")
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        
        counter = 1
        for ch_id, ch_link in CHANNELS.items():
            try:
                member = await bot.get_chat_member(chat_id=ch_id, user_id=message.from_user.id)
                if member.status in ["left", "kicked"]:
                    keyboard.add(types.InlineKeyboardButton(
                        text=f"📢 {counter}-kanalga a'zo bo'lish", 
                        url=ch_link
                    ))
                    counter += 1
            except:
                keyboard.add(types.InlineKeyboardButton(
                    text=f"📢 {counter}-kanalga a'zo bo'lish", 
                    url=ch_link
                ))
                counter += 1
        
        keyboard.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check"))
        await message.answer("⚠️ Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:", reply_markup=keyboard)

# 3. Tekshirish tugmasi uchun handler
@dp.callback_query_handler(text="check")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("✅ Rahmat! Obuna tasdiqlandi. Kino kodini yuborishingiz mumkin.")
    else:
        await call.answer("❌ Hali hamma kanallarga a'zo bo'lmadingiz!", show_alert=True)

# Kino qidirish va boshqa handlerlar (pastda qolishi kerak)
@dp.message_handler()
async def get_movie(message: types.Message):
    # Kino qidirish kodi...
    pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
