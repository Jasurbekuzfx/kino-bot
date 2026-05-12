import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database import create_db, add_movie, get_movie
import config

bot = Bot(token=config.TOKEN)
dp = Dispatcher()

# Kanallarga a'zolikni tekshirish funksiyasi
async def check_sub(user_id):
    for channel in config.CHANNELS:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        if member.status == "left":
            return False
    return True

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    is_sub = await check_sub(message.from_user.id)
    
    if is_sub:
        await message.answer(f"👋 Salom {message.from_user.full_name}!\nKino kodini kiriting:")
    else:
        builder = InlineKeyboardBuilder()
        builder.row(types.InlineKeyboardButton(text="📢 Kanalga a'zo bo'lish", url="https://t.me/+SrertxiwC0Y0ZDhi"))
        builder.row(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub"))
        
        await message.answer(
            "⚠️ Botdan foydalanish uchun kanalimizga a'zo bo'lishingiz kerak:",
            reply_markup=builder.as_markup()
        )

@dp.callback_query(F.data == "check_sub")
async def callback_check(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("✅ Rahmat! Endi kino kodini yuborishingiz mumkin.")
    else:
        await call.answer("❌ Hali a'zo bo'lmadingiz!", show_alert=True)

# Kino qidirish (Faqat raqam yozilsa ishlaydi)
@dp.message(F.text.isdigit())
async def search_movie(message: types.Message):
    if not await check_sub(message.from_user.id):
        return await cmd_start(message)
    
    movie = get_movie(message.text)
    if movie:
        title, file_id = movie
        await bot.send_video(
            chat_id=message.chat.id,
            video=file_id,
            caption=f"🎬 Nomi: {title}\n🆔 Kodi: {message.text}\n\n✨ @Kino_Bot_Sizniki" # Bu yerga botingiz userneymini yozing
        )
    else:
        await message.answer("😔 Kechirasiz, bu kod bilan kino topilmadi.")

async def main():
    create_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
