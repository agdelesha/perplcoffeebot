from aiogram import types
from aiogram.types import InputFile
from ..config.config import WELCOME_IMAGE
from ..keyboards.keyboards import get_client_keyboard
from ..utils.helpers import load_users, save_user

async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users:
        save_user(user_id)
        users.add(user_id)

    welcome_text = """
привет, пипл! 
добро пожаловать в пёрпл!
ваша любимая кофейня теперь в вашем кармане 💜

копите бонусы за каждый заказ (1 заказ = 1 бонус) и обменивайте 6 бонусов на бесплатный напиток 

всегда ждём вас 💫
"""
    with open(WELCOME_IMAGE, 'rb') as photo:
        await message.bot.send_photo(
            chat_id=message.chat.id,
            photo=InputFile(photo),
            caption=welcome_text,
            reply_markup=get_client_keyboard()
        )

async def cmd_help(message: types.Message):
    help_text = """
На связи ПЁРПЛ! ☕️

Как это работает:

Сделайте заказ в нашей кофейне
Нажмите "Начислить бонусы" в боте
Бариста подтвердит начисление
Бонусы появятся на вашем счете

Накопив 6 бонусов вы сможете их потратить на любой напиток из классического меню!
Нажмите "Обменять бонусы на напиток"
Бариста подтвердит обмен
Бонусы спишутся
Бонусы можно обменять на любой средний напиток из классического меню
За остальные напитки(большого объема или из фирменного меню) доплата 70р

Посмотреть количество накопленных бонусов вы можете нажав кнопку "Проверить баланс"

Наслаждайтесь любимыми напитками и копите бонусы с ПЁРПЛ! 💜
"""
    await message.reply(help_text, reply_markup=get_client_keyboard())

async def about_coffee_shop(message: types.Message):
    about_text = """
ПЁРПЛ - это кофейня с уютной атмосферой и вкусным кофе 💜

Мы находимся по адресу: Москва, Большая Семёновская 27к2
Время работы: 8:00-20:00

Для связи:
Телефон: +7(977)999-99-99
Telegram: @purplecoffee

Мы всегда рады видеть вас! ✨
"""
    await message.reply(about_text)
