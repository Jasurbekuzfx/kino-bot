import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, ADMINS, CHANNELS, INVITE_LINK
import database as db
from aiohttp import web

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Render serveri uchun Health Check
async def handle(request):
    return web.Response(text="Bot is running!")

app = web.Application()
app.router.add_get("/", handle)

async def check_sub(user_id):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception:
            return False
    return True

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    db.add_user(message.from_user.id)
    
    # Obunani tekshirish
    not_subbed = []
    for ch_id in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=message.from_user.id)
            if member.status in ["left", "kicked"]:
                not_subbed.append(ch_id)
        except:
            not_subbed.append(ch_id)

    if not not_subbed:
        await message.answer(f"🎬 Salom {message.from_user.first_name}!\nKino kodini yuboring:")
    else:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        
        # Har bir a'zo bo'linmagan kanal uchun alohida tugma
        for i, ch_id in enumerate(not_subbed, 1):
            keyboard.add(types.InlineKeyboardButton(
                text=f"📢 {i}-kanalga a'zo bo'lish", 
                url=CHANNELS[ch_id]
            ))
        
        keyboard.add(types.InlineKeyboardButton(text="✅ Tekshirish", callback_data="check"))
        await message.answer("⚠️ Botdan foydalanish uchun quyidagi kanallarga a'zo bo'ling:", reply_markup=keyboard)
@dp.callback_query_handler(text="check")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("✅ Rahmat! Kino kodini yuboring:")
    else:
        await call.answer("❌ Siz hali kanalga a'zo emassiz!", show_alert=True)

@dp.message_handler(content_types=['video'])
async def save_movie(message: types.Message):
    # Admin ekanligingizni tekshirish uchun log chiqaradi
    logging.info(f"Video keldi. User ID: {message.from_user.id}")
    
    if message.from_user.id not in ADMINS:
        logging.warning("Bu foydalanuvchi admin emas!")
        return

    if message.caption:
        caption = message.caption.lower()
        if "kino:" in caption:
            try:
                parts = message.caption.split(":")
                code = parts[1].strip()
                title = parts[2].strip()
                
                if db.add_movie(code, title, message.video.file_id):
                    await message.reply(f"✅ Saqlandi!\nKod: {code}\nNomi: {title}")
                else:
                    await message.reply("❌ Bu kod bazada band.")
            except Exception as e:
                logging.error(f"Xatolik: {e}")
                await message.reply("⚠️ Format xato! Namuna: kino:100:Forsaj")

@dp.message_handler(lambda message: message.text.isdigit())
async def search_movie(message: types.Message):
    if not await check_sub(message.from_user.id):
        return await start_cmd(message)
    
    res = db.get_movie(message.text)
    if res:
        await bot.send_video(message.chat.id, res[1], caption=f"🎬 {res[0]}")
    else:
        await message.answer("😔 Bu kod bilan kino topilmadi.")

async def on_startup(x):
    db.create_db()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000)))
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
