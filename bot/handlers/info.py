from aiogram import types
from aiogram.types import InputFile
from bot.keyboards.keyboards import get_client_keyboard
from bot.database.db import save_user, load_users
from bot.config.config import WELCOME_IMAGE, ABOUT_IMAGE
import os

async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        save_user(user_id)
        users.add(user_id)

    # Подготовка текста приветственного сообщения
    welcome_text = """
привет, пипл! 
добро пожаловать в пёрпл!
ваша любимая кофейня теперь в вашем кармане 💜

копите бонусы за каждый заказ (1 заказ = 1 бонус) и обменивайте 6 бонусов на бесплатный напиток 

всегда ждём вас 💫
"""

    # Отправка фото с подписью
    with open(WELCOME_IMAGE, 'rb') as photo:
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=InputFile(photo),
            caption=welcome_text,
            reply_markup=get_client_keyboard()
        )

async def about_coffee_shop(message: types.Message):
    about_text = """
Санкт-Петербург

📍11-я Красноармейская 11, стр 3
📍Гороховая 55

пн-пт 8:00-20:00
сб-вс 9:00-21:00

💫 предлагаем широкий выбор кофейных (и не только) напитков, сладостей и перекусов, а также уютную атмосферу для наших гостей 

обожаем все фиолетовое (<tg-spoiler>как и наш основатель</tg-spoiler>), но рады разбавлять будни Питера яркими акцентами - наша желтая кофемашина не может не привлекать на себя внимание

ждём вас в пёрпл! 💜

будем рады вашим отзывам здесь: http://surl.li/yceozo
"""
    with open(ABOUT_IMAGE, 'rb') as photo:
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=InputFile(photo),
            caption=about_text,
            parse_mode="HTML"
        )
