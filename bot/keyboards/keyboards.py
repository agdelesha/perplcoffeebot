from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

def get_client_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("💰 Начислить бонусы"))
    keyboard.row(
        KeyboardButton("📊 Проверить баланс"), 
        KeyboardButton("☕ Обменять бонусы на напиток")
    )
    keyboard.row(
        KeyboardButton("🏠 О кофейне"), 
        KeyboardButton("📋 Меню")
    )
    return keyboard

def get_subscription_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Конечно, я не против!", callback_data="accept_subscription"),
        InlineKeyboardButton("А можно не надо?", callback_data="reject_subscription")
    )
    return keyboard

def get_bonus_word(bonus):
    if bonus % 10 == 1 and bonus % 100 != 11:
        return "бонус"
    elif 2 <= bonus % 10 <= 4 and (bonus % 100 < 10 or bonus % 100 >= 20):
        return "бонуса"
    else:
        return "бонусов"

def get_bonus_confirmation_keyboard(request_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("1️⃣ 1 бонус", callback_data=f"b1_{request_id}"),
        InlineKeyboardButton("2️⃣ 2 бонуса", callback_data=f"b2_{request_id}")
    )
    keyboard.row(
        InlineKeyboardButton("3️⃣ 3 бонуса", callback_data=f"b3_{request_id}"),
        InlineKeyboardButton("4️⃣ 4 бонуса", callback_data=f"b4_{request_id}")
    )
    keyboard.row(
        InlineKeyboardButton("5️⃣ 5 бонусов", callback_data=f"b5_{request_id}"),
        InlineKeyboardButton("6️⃣ 6 бонусов", callback_data=f"b6_{request_id}")
    )
    keyboard.row(
        InlineKeyboardButton("❌ Отклонить", callback_data=f"br_{request_id}")
    )
    return keyboard

def get_exchange_confirmation_keyboard(user_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"ex_ok_{user_id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"ex_no_{user_id}")
    )
    return keyboard

def get_location_keyboard():
    """Клавиатура выбора локации для начисления бонусов"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("11-я Красноармейская", callback_data="loc_kr"),
        InlineKeyboardButton("Гороховая", callback_data="loc_gr")
    )
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return keyboard

def get_exchange_location_keyboard():
    """Клавиатура выбора локации для обмена бонусов"""
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("11-я Красноармейская", callback_data="ex_loc_kr"),
        InlineKeyboardButton("Гороховая", callback_data="ex_loc_gr")
    )
    keyboard.add(InlineKeyboardButton("❌ Отмена", callback_data="cancel"))
    return keyboard

def get_admin_keyboard():
    """Клавиатура админ-панели"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("👑 Управление админами"))
    keyboard.row(KeyboardButton("💫 Бонусы вручную"))
    keyboard.row(KeyboardButton("✉️ Отправить сообщение"))
    keyboard.row(KeyboardButton("↩️ Вернуться в обычное меню"))
    return keyboard
