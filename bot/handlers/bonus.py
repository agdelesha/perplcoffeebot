from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import exceptions
from aiogram.utils.exceptions import MessageNotModified
from bot.keyboards.keyboards import (
    get_client_keyboard, get_bonus_confirmation_keyboard,
    get_exchange_confirmation_keyboard, get_location_keyboard, get_exchange_location_keyboard
)
from bot.database.db import get_user_bonuses, update_user_bonuses
from bot.config.config import BARISTA_CHAT_ID, GOROHOVAYA_CHAT_ID, BONUSES_FOR_DRINK

import uuid
import asyncio
import logging
import os
import random
from aiogram.types import InputFile
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальные переменные для отслеживания запросов
user_requests = {}
processed_bonuses = set()
processed_exchanges = set()  # Добавляем новый set для отслеживания обмененных бонусов
lock = asyncio.Lock()

# Максимальное количество бонусов, которое можно начислить за раз
MAX_BONUS_AMOUNT = 100

# Путь к папке с изображениями
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'images')

# В начале файла добавляем словарь для хранения информации об обработанных запросах
processed_requests_info = {}

def get_random_image() -> str:
    """Получить случайное изображение из папки images"""
    images = [f for f in os.listdir(IMAGES_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        return None
    return os.path.join(IMAGES_DIR, random.choice(images))

async def show_location_choice(message: types.Message):
    user_id = message.from_user.id
    
    # Проверяем, есть ли уже активный запрос у пользователя
    if user_id in user_requests:
        await message.answer("❌ У вас уже есть активный запрос на начисление бонусов. Дождитесь его обработки.")
        return
    
    keyboard = get_location_keyboard()
    await message.answer("В какой кофейне вы сделали заказ?", reply_markup=keyboard)

async def request_bonus_krasnoarmeyskaya(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Проверяем, есть ли уже активный запрос у пользователя
    if user_id in user_requests:
        logger.warning(f"User {user_id} already has an active request")
        await callback_query.message.answer("❌ У вас уже есть активный запрос на начисление бонусов. Дождитесь его обработки.")
        return
    
    # Создаем уникальный ID для запроса
    request_id = str(uuid.uuid4())
    username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "без username"
    
    logger.info(f"Creating new bonus request for user {user_id} (Красноармейская), request_id: {request_id}")
    
    # Сохраняем информацию о запросе
    user_requests[user_id] = {
        'request_id': request_id,
        'timestamp': datetime.now(),
        'message_id': callback_query.message.message_id,
        'location': 'Красноармейская',
        'username': username,
        'full_name': callback_query.from_user.full_name
    }
    
    # Создаем клавиатуру для подтверждения
    keyboard = get_bonus_confirmation_keyboard(request_id)
    
    # Отправляем запрос баристе
    notification_text = (
        f"Запрос на начисление бонусов (Красноармейская)\n"
        f"От: {callback_query.from_user.full_name} ({callback_query.from_user.id})\n"
        f"Username: {username}\n"
        f"Текущий баланс: {get_user_bonuses(user_id)} бонусов"
    )
    
    try:
        await callback_query.bot.send_message(
            BARISTA_CHAT_ID,
            notification_text,
            reply_markup=keyboard
        )
        logger.info(f"Sent bonus request to barista chat for user {user_id}")
        
        await callback_query.message.edit_text(
            "✅ Запрос на начисление бонусов отправлен\n"
            "Ожидайте подтверждения от бариста..."
        )
    except Exception as e:
        logger.error(f"Error sending bonus request for user {user_id}: {e}")
        # В случае ошибки удаляем информацию о запросе
        if user_id in user_requests:
            del user_requests[user_id]
            logger.info(f"Removed failed request for user {user_id}")
        
        await callback_query.message.edit_text(
            "❌ Произошла ошибка при отправке запроса. Попробуйте позже."
        )

async def request_bonus_gorohovaya(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    
    # Проверяем, есть ли уже активный запрос у пользователя
    if user_id in user_requests:
        logger.warning(f"User {user_id} already has an active request")
        await callback_query.message.answer("❌ У вас уже есть активный запрос на начисление бонусов. Дождитесь его обработки.")
        return
    
    # Создаем уникальный ID для запроса
    request_id = str(uuid.uuid4())
    username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "без username"
    
    logger.info(f"Creating new bonus request for user {user_id} (Гороховая), request_id: {request_id}")
    
    # Сохраняем информацию о запросе
    user_requests[user_id] = {
        'request_id': request_id,
        'timestamp': datetime.now(),
        'message_id': callback_query.message.message_id,
        'location': 'Гороховая',
        'username': username,
        'full_name': callback_query.from_user.full_name
    }
    
    # Создаем клавиатуру для подтверждения
    keyboard = get_bonus_confirmation_keyboard(request_id)
    
    # Отправляем запрос баристе
    notification_text = (
        f"Запрос на начисление бонусов (Гороховая)\n"
        f"От: {callback_query.from_user.full_name} ({callback_query.from_user.id})\n"
        f"Username: {username}\n"
        f"Текущий баланс: {get_user_bonuses(user_id)} бонусов"
    )
    
    try:
        await callback_query.bot.send_message(
            GOROHOVAYA_CHAT_ID,
            notification_text,
            reply_markup=keyboard
        )
        logger.info(f"Sent bonus request to barista chat for user {user_id}")
        
        await callback_query.message.edit_text(
            "✅ Запрос на начисление бонусов отправлен\n"
            "Ожидайте подтверждения от бариста..."
        )
    except Exception as e:
        logger.error(f"Error sending bonus request for user {user_id}: {e}")
        # В случае ошибки удаляем информацию о запросе
        if user_id in user_requests:
            del user_requests[user_id]
            logger.info(f"Removed failed request for user {user_id}")
        
        await callback_query.message.edit_text(
            "❌ Произошла ошибка при отправке запроса. Попробуйте позже."
        )

async def process_bonus(callback_query: types.CallbackQuery, bonus_amount: int):
    """Общая функция для обработки бонусов"""
    await callback_query.answer()
    
    # Получаем данные из callback_data
    _, request_id = callback_query.data.split('_')
    logger.info(f"Processing bonus request: {request_id}, amount: {bonus_amount}")
    
    # Ищем пользователя по request_id
    user_id = None
    username = None
    full_name = None
    
    # Проверяем, есть ли информация в processed_requests_info
    if request_id in processed_requests_info:
        info = processed_requests_info[request_id]
        user_id = info['user_id']
        username = info['username']
        full_name = info['full_name']
    else:
        # Если нет, ищем в user_requests
        for uid, request_data in user_requests.items():
            if request_data.get('request_id') == request_id:
                user_id = uid
                username = request_data.get('username', 'без username')
                full_name = request_data.get('full_name', 'Неизвестный пользователь')
                # Сохраняем информацию для будущего использования
                processed_requests_info[request_id] = {
                    'user_id': user_id,
                    'username': username,
                    'full_name': full_name,
                    'bonus_amount': bonus_amount
                }
                break
    
    # Проверяем, не был ли этот запрос уже обработан
    if request_id in processed_bonuses:
        logger.warning(f"Request {request_id} already processed")
        try:
            bonus_word = get_bonus_word(bonus_amount)
            await callback_query.message.edit_text(
                f"❌ Этот запрос уже был обработан\n\n"
                f"👤 Пользователь: {full_name} ({user_id})\n"
                f"Username: {username}\n"
                f"💫 Начислено: {bonus_amount} {bonus_word}"
            )
        except MessageNotModified:
            pass
        return

    async with lock:
        if request_id in processed_bonuses:
            logger.warning(f"Request {request_id} already processed (double-check)")
            try:
                bonus_word = get_bonus_word(bonus_amount)
                await callback_query.message.edit_text(
                    f"❌ Этот запрос уже был обработан\n\n"
                    f"👤 Пользователь: {full_name} ({user_id})\n"
                    f"Username: {username}\n"
                    f"💫 Начислено: {bonus_amount} {bonus_word}"
                )
            except MessageNotModified:
                pass
            return
            
        processed_bonuses.add(request_id)
        logger.info(f"Added request {request_id} to processed_bonuses")
    
    if user_id is None:
        logger.error(f"Request {request_id} not found in user_requests. Current requests: {user_requests}")
        try:
            await callback_query.message.edit_text("❌ Запрос не найден или устарел")
        except MessageNotModified:
            pass
        return
    
    logger.info(f"Found user_id {user_id} for request {request_id}")
    
    # Обновляем бонусы пользователя
    current_bonuses = get_user_bonuses(user_id)
    new_bonuses = current_bonuses + bonus_amount
    update_user_bonuses(user_id, new_bonuses)
    logger.info(f"Updated bonuses for user {user_id}: {current_bonuses} -> {new_bonuses}")
    
    # Отправляем сообщение пользователю
    bonus_word = get_bonus_word(bonus_amount)
    user_message = (
        f"✅ Вам начислено {bonus_amount} {bonus_word}!\n"
        f"Теперь у вас {new_bonuses} {get_bonus_word(new_bonuses)}"
    )
    
    try:
        await callback_query.bot.send_message(user_id, user_message)
        logger.info(f"Sent bonus confirmation to user {user_id}")
    except Exception as e:
        logger.error(f"Error sending message to user {user_id}: {e}")
    
    # Обновляем сообщение баристе с информацией о пользователе
    original_message = callback_query.message.text.split('\n')[0]  # Сохраняем первую строку исходного сообщения
    try:
        await callback_query.message.edit_text(
            f"{original_message}\n\n"
            f"✅ Начислено {bonus_amount} {bonus_word}\n"
            f"👤 Пользователь: {full_name} ({user_id})\n"
            f"Username: {username}\n"
            f"💫 Баланс: {new_bonuses} {get_bonus_word(new_bonuses)}"
        )
    except MessageNotModified:
        pass
    
    # Удаляем обработанный запрос
    if user_id in user_requests:
        del user_requests[user_id]
        logger.info(f"Removed request for user {user_id}")

async def process_one_bonus(callback_query: types.CallbackQuery):
    await process_bonus(callback_query, 1)

async def process_two_bonus(callback_query: types.CallbackQuery):
    await process_bonus(callback_query, 2)

async def process_three_bonus(callback_query: types.CallbackQuery):
    await process_bonus(callback_query, 3)

async def process_four_bonus(callback_query: types.CallbackQuery):
    await process_bonus(callback_query, 4)

async def process_five_bonus(callback_query: types.CallbackQuery):
    await process_bonus(callback_query, 5)

async def process_six_bonus(callback_query: types.CallbackQuery):
    """Обработчик начисления 6 бонусов"""
    await process_bonus(callback_query, 6)

async def process_bonus_rejection(callback_query: types.CallbackQuery):
    await callback_query.answer()
    request_id = callback_query.data.replace('br_', '')
    
    # Находим пользователя по request_id
    user_id = None
    for uid, request_info in user_requests.items():
        if request_info['request_id'] == request_id:
            user_id = uid
            break
    
    if not user_id or request_id in processed_bonuses:
        await safe_edit_message(callback_query.message, "❌ Этот запрос уже был обработан или устарел.")
        return
    
    # Отмечаем запрос как обработанный
    processed_bonuses.add(request_id)
    
    # Удаляем информацию о запросе
    if user_id in user_requests:
        del user_requests[user_id]
        print(f"DEBUG: Удален активный запрос для user_id: {user_id}")
    
    # Отправляем уведомление пользователю
    try:
        await callback_query.bot.send_message(
            user_id,
            "❌ Запрос на начисление бонусов отклонен."
        )
    except Exception as e:
        print(f"Ошибка при отправке уведомления пользователю: {e}")
    
    # Обновляем сообщение баристы
    await safe_edit_message(callback_query.message, f"{callback_query.message.text}\n\n❌ Запрос отклонен")

async def check_balance(message: types.Message):
    user_id = message.from_user.id
    bonuses = get_user_bonuses(user_id)
    await message.answer(f"Ваш текущий баланс: {bonuses} бонусов")

async def exchange_bonus(message: types.Message):
    user_id = message.from_user.id
    current_bonuses = get_user_bonuses(user_id)
    
    if current_bonuses < BONUSES_FOR_DRINK:
        await message.answer(
            f"❌ К сожалению, у вас недостаточно бонусов.\n"
            f"Необходимо {BONUSES_FOR_DRINK} бонусов, у вас {current_bonuses} бонусов."
        )
        return
    
    keyboard = get_exchange_location_keyboard()
    await message.answer("Выберите кофейню для обмена бонусов:", reply_markup=keyboard)

async def process_exchange_krasnoarmeyskaya(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    current_bonuses = get_user_bonuses(user_id)
    
    # Проверяем достаточность бонусов
    if current_bonuses < BONUSES_FOR_DRINK:
        await callback_query.message.edit_text(
            f"❌ К сожалению, у вас недостаточно бонусов.\n"
            f"Необходимо {BONUSES_FOR_DRINK} бонусов, у вас {current_bonuses} бонусов."
        )
        return
    
    # Обновляем баланс
    new_bonuses = current_bonuses - BONUSES_FOR_DRINK
    update_user_bonuses(user_id, new_bonuses)
    
    # Подготавливаем текст сообщения
    message_text = (
        "🎉 Поздравляем! Ваши бонусы обменяны на напиток! 🎊\n\n"
        "☕️ Вы можете выбрать любой средний напиток с любыми добавками!\n"
        "📍 Кофейня: Красноармейская\n\n"
        "🎯 Покажите это сообщение бариста\n\n"
        f"💫 Остаток бонусов: {new_bonuses}"
    )
    
    try:
        # Пытаемся отправить сообщение с фото
        kit_number = random.randint(1, 12)
        image_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'images', f'kit{kit_number}.jpg')
        
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await callback_query.bot.send_photo(
                    user_id,
                    photo,
                    caption=message_text
                )
        else:
            # Если файл не найден, отправляем просто текст
            await callback_query.message.answer(message_text)
    except Exception as e:
        # В случае любой ошибки, отправляем просто текст
        await callback_query.message.answer(message_text)
    
    # Отправляем уведомление в чат бариста
    username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "без username"
    notification_text = (
        f"🔄 Обмен бонусов на напиток (Красноармейская)\n"
        f"От: {callback_query.from_user.full_name} ({callback_query.from_user.id})\n"
        f"Username: {username}"
    )
    
    try:
        await callback_query.bot.send_message(BARISTA_CHAT_ID, notification_text)
    except Exception as e:
        print(f"Ошибка при отправке уведомления баристам: {e}")
    
    # Удаляем сообщение с выбором локации
    await callback_query.message.delete()

async def process_exchange_gorohovaya(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    current_bonuses = get_user_bonuses(user_id)
    
    # Проверяем достаточность бонусов
    if current_bonuses < BONUSES_FOR_DRINK:
        await callback_query.message.edit_text(
            f"❌ К сожалению, у вас недостаточно бонусов.\n"
            f"Необходимо {BONUSES_FOR_DRINK} бонусов, у вас {current_bonuses} бонусов."
        )
        return
    
    # Обновляем баланс
    new_bonuses = current_bonuses - BONUSES_FOR_DRINK
    update_user_bonuses(user_id, new_bonuses)
    
    # Подготавливаем текст сообщения
    message_text = (
        "🎉 Поздравляем! Ваши бонусы обменяны на напиток! 🎊\n\n"
        "☕️ Вы можете выбрать любой средний напиток с любыми добавками!\n"
        "📍 Кофейня: Гороховая\n\n"
        "🎯 Покажите это сообщение бариста\n\n"
        f"💫 Остаток бонусов: {new_bonuses}"
    )
    
    try:
        # Пытаемся отправить сообщение с фото
        kit_number = random.randint(1, 12)
        image_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'images', f'kit{kit_number}.jpg')
        
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await callback_query.bot.send_photo(
                    user_id,
                    photo,
                    caption=message_text
                )
        else:
            # Если файл не найден, отправляем просто текст
            await callback_query.message.answer(message_text)
    except Exception as e:
        # В случае любой ошибки, отправляем просто текст
        await callback_query.message.answer(message_text)
    
    # Отправляем уведомление в чат бариста
    username = f"@{callback_query.from_user.username}" if callback_query.from_user.username else "без username"
    notification_text = (
        f"🔄 Обмен бонусов на напиток (Гороховая)\n"
        f"От: {callback_query.from_user.full_name} ({callback_query.from_user.id})\n"
        f"Username: {username}"
    )
    
    try:
        await callback_query.bot.send_message(GOROHOVAYA_CHAT_ID, notification_text)
    except Exception as e:
        print(f"Ошибка при отправке уведомления баристам: {e}")
    
    # Удаляем сообщение с выбором локации
    await callback_query.message.delete()

async def process_exchange_confirmation(callback_query: types.CallbackQuery):
    await callback_query.answer()
    
    # Получаем данные из callback_data
    _, user_id = callback_query.data.split('_')[1:]
    user_id = int(user_id)
    
    # Проверяем, не был ли этот обмен уже обработан
    exchange_id = f"{user_id}_{int(datetime.now().timestamp())}"
    if exchange_id in processed_exchanges:
        await callback_query.message.edit_text("❌ Этот запрос уже был обработан")
        return
        
    processed_exchanges.add(exchange_id)
    
    # Проверяем баланс пользователя
    current_bonuses = get_user_bonuses(user_id)
    
    if current_bonuses < BONUSES_FOR_DRINK:
        await callback_query.message.edit_text(
            f"❌ Недостаточно бонусов. Необходимо {BONUSES_FOR_DRINK} бонусов."
        )
        return
    
    # Списываем бонусы
    new_bonuses = current_bonuses - BONUSES_FOR_DRINK
    update_user_bonuses(user_id, new_bonuses)
    
    # Получаем случайное изображение
    image_path = get_random_image()
    
    # Отправляем сообщение пользователю
    try:
        message_text = (
            f"✅ Вы успешно обменяли {BONUSES_FOR_DRINK} бонусов на напиток!\n"
            f"Покажите это сообщение бариста\n"
            f"Остаток бонусов: {new_bonuses}"
        )
        
        if image_path:
            # Отправляем сообщение с картинкой
            photo = InputFile(image_path)
            await callback_query.bot.send_photo(
                user_id,
                photo=photo,
                caption=message_text
            )
        else:
            # Если картинка не найдена, отправляем только текст
            await callback_query.bot.send_message(user_id, message_text)
            
    except Exception as e:
        logger.error(f"Error sending exchange confirmation to user {user_id}: {e}")
    
    # Обновляем сообщение баристы
    await callback_query.message.edit_text("✅ Бонусы успешно обменяны на напиток")

async def process_exchange_rejection(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = int(callback_query.data.split('_')[1])
    
    # Проверяем, не был ли уже обработан этот обмен
    if user_id in processed_exchanges:
        await safe_edit_message(callback_query.message, "Этот обмен уже был обработан")
        return
    
    processed_exchanges.add(user_id)
    await safe_edit_message(callback_query.message, "Обмен бонусов отменен")

async def safe_edit_message(message, new_text):
    """
    Безопасное редактирование сообщения с обработкой ошибки MessageNotModified
    """
    try:
        await message.edit_text(new_text)
    except MessageNotModified:
        # Игнорируем ошибку, так как сообщение уже содержит нужный текст
        pass

def get_bonus_word(count):
    """Возвращает правильное склонение слова 'бонус' в зависимости от числа"""
    if count % 10 == 1 and count % 100 != 11:
        return "бонус"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return "бонуса"
    else:
        return "бонусов"

__all__ = [
    'show_location_choice', 'request_bonus_krasnoarmeyskaya',
    'request_bonus_gorohovaya', 'process_one_bonus', 'process_two_bonus',
    'process_three_bonus', 'process_four_bonus', 'process_five_bonus',
    'process_six_bonus', 'process_bonus_rejection', 'BonusConfirmation',
    'check_balance', 'exchange_bonus',
    'process_exchange_confirmation', 'process_exchange_rejection',
    'process_exchange_krasnoarmeyskaya', 'process_exchange_gorohovaya'
]

class BonusConfirmation(StatesGroup):
    waiting_for_amount = State()