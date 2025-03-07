from aiogram.utils.exceptions import MessageNotModified
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
import asyncio
import logging
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.config.config import API_TOKEN
from bot.database.db import init_db, clear_old_requests
from bot.handlers.bonus import (
    show_location_choice, request_bonus_krasnoarmeyskaya,
    request_bonus_gorohovaya, process_one_bonus, process_two_bonus,
    process_three_bonus, process_four_bonus, process_five_bonus,
    process_six_bonus, process_bonus_rejection, BonusConfirmation,
    check_balance, exchange_bonus,
    process_exchange_confirmation, process_exchange_rejection,
    process_exchange_krasnoarmeyskaya, process_exchange_gorohovaya,
)
from bot.handlers.menu import send_menu
from bot.handlers.info import cmd_start, about_coffee_shop
from bot.handlers.admin import (
    admin_command, 
    process_admin_user, 
    process_admin_id,
    process_manual_bonus, 
    process_bonus_user_id, 
    process_bonus_amount,
    process_send_message, 
    process_message_user_id, 
    process_message_text,
    AdminStates, 
    return_to_main_menu, 
    cancel_admin_action
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def cancel_action(callback_query: types.CallbackQuery, state: FSMContext):
    """Отмена действия"""
    await state.finish()
    await callback_query.message.edit_text("❌ Действие отменено")
    await callback_query.answer()

def register_handlers(dp: Dispatcher):
    # Команды
    dp.register_message_handler(cmd_start, commands=['start'])
    dp.register_message_handler(admin_command, commands=['admin'])
    
    # Обработчики кнопок основного меню
    dp.register_message_handler(show_location_choice, lambda msg: msg.text == "💰 Начислить бонусы")
    dp.register_message_handler(about_coffee_shop, lambda msg: msg.text == "🏠 О кофейне")
    dp.register_message_handler(send_menu, lambda msg: msg.text == "📋 Меню")
    dp.register_message_handler(check_balance, lambda msg: msg.text == "📊 Проверить баланс")
    dp.register_message_handler(exchange_bonus, lambda msg: msg.text == "☕ Обменять бонусы на напиток")
    
    # Обработчики локаций для бонусов
    dp.register_callback_query_handler(
        request_bonus_krasnoarmeyskaya,
        lambda c: c.data == "loc_kr"
    )
    dp.register_callback_query_handler(
        request_bonus_gorohovaya,
        lambda c: c.data == "loc_gr"
    )
    
    # Обработчики локаций для обмена бонусов
    dp.register_callback_query_handler(
        process_exchange_krasnoarmeyskaya,
        lambda c: c.data == "ex_loc_kr"
    )
    dp.register_callback_query_handler(
        process_exchange_gorohovaya,
        lambda c: c.data == "ex_loc_gr"
    )
    
    # Обработчики подтверждения бонусов
    dp.register_callback_query_handler(
        process_one_bonus,
        lambda c: c.data and c.data.startswith('b1_')
    )
    dp.register_callback_query_handler(
        process_two_bonus,
        lambda c: c.data and c.data.startswith('b2_')
    )
    dp.register_callback_query_handler(
        process_three_bonus,
        lambda c: c.data and c.data.startswith('b3_')
    )
    dp.register_callback_query_handler(
        process_four_bonus,
        lambda c: c.data and c.data.startswith('b4_')
    )
    dp.register_callback_query_handler(
        process_five_bonus,
        lambda c: c.data and c.data.startswith('b5_')
    )
    dp.register_callback_query_handler(
        process_six_bonus,
        lambda c: c.data and c.data.startswith('b6_')
    )
    dp.register_callback_query_handler(
        process_bonus_rejection,
        lambda c: c.data and c.data.startswith('br_')
    )
    
    # Обработчики обмена бонусов
    dp.register_callback_query_handler(
        process_exchange_confirmation,
        lambda c: c.data and c.data.startswith('ex_ok_')
    )
    dp.register_callback_query_handler(
        process_exchange_rejection,
        lambda c: c.data and c.data.startswith('ex_no_')
    )
    
    # Обработчик ввода количества бонусов
    dp.register_message_handler(
        process_bonus_amount,
        state=BonusConfirmation.waiting_for_amount
    )
    
    # Обработчик отмены
    dp.register_callback_query_handler(
        cancel_action,
        lambda c: c.data == "cancel",
        state="*"
    )
    
    # Обработчик отмены для админских действий
    dp.register_message_handler(
        cancel_admin_action,
        lambda msg: msg.text == "❌ Отменить",
        state=[
            AdminStates.waiting_for_admin_id,
            AdminStates.waiting_for_bonus_user_id,
            AdminStates.waiting_for_bonus_amount,
            AdminStates.waiting_for_message_user_id,
            AdminStates.waiting_for_message_text
        ]
    )
    
    # Обработчики админ-панели
    dp.register_message_handler(
        process_admin_user,
        lambda msg: msg.text == "👑 Управление админами"
    )
    dp.register_message_handler(
        process_manual_bonus,
        lambda msg: msg.text == "💫 Бонусы вручную"
    )
    dp.register_message_handler(
        process_send_message,
        lambda msg: msg.text == "✉️ Отправить сообщение"
    )
    dp.register_message_handler(
        return_to_main_menu,
        lambda msg: msg.text == "↩️ Вернуться в обычное меню"
    )
    
    # Обработчики состояний админ-панели
    dp.register_message_handler(
        process_admin_id,
        state=AdminStates.waiting_for_admin_id
    )
    dp.register_message_handler(
        process_bonus_user_id,
        state=AdminStates.waiting_for_bonus_user_id
    )
    dp.register_message_handler(
        process_bonus_amount,
        state=AdminStates.waiting_for_bonus_amount
    )
    dp.register_message_handler(
        process_message_user_id,
        state=AdminStates.waiting_for_message_user_id
    )
    dp.register_message_handler(
        process_message_text,
        state=AdminStates.waiting_for_message_text
    )

register_handlers(dp)

async def on_startup(dp):
    # Инициализация базы данных
    init_db()
    
    # Запуск периодической очистки старых запросов
    asyncio.create_task(periodic_cleanup())

async def periodic_cleanup():
    while True:
        clear_old_requests()
        await asyncio.sleep(24 * 60 * 60)  # Очистка раз в сутки

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
