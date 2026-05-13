import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN, ADMINS, CHANNELS, INVITE_LINK
import database as db
from aiohttp import web

# Logging sozlash
logging.basicConfig(level=logging.INFO)

# Botni ishga tushirish
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Render uchun oddiy Web Server (Health Check uchun)
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
    # Admin tekshiruvi va caption formati: kino:kod:nomi
    if message.from_user.id in ADMINS and message.caption and message.caption.startswith("kino:"):
        try:
            parts = message.caption.split(":")
            code = parts[1]
            title = parts[2]
            if db.add_movie(code, title, message.video.file_id):
                await message.reply(f"✅ Saqlandi! Kod: {code}")
            else:
                await message.reply("❌ Bu kod bazada mavjud.")
        except IndexError:
            await message.reply("⚠️ Format xato! Namuna: kino:123:Forsaj")

@dp.message_handler(lambda message: message.text.isdigit())
async def search_movie(message: types.Message):
    if not await check_sub(message.from_user.id):
        return await start_cmd(message)
    
    res = db.get_movie(message.text)
    if res:
        # res[0] - title, res[1] - file_id
        await bot.send_video(message.chat.id, res[1], caption=f"🎬 {res[0]}")
    else:
        await message.answer("😔 Bu kod bilan kino topilmadi.")

async def on_startup(x):
    db.create_db()
    # Render portini ochish
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 10000)))
    await site.start()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
