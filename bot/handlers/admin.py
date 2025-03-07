from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from bot.config.config import ADMIN_ID
from bot.database.db import (
    is_admin, add_admin, remove_admin,
    get_user_bonuses, update_user_bonuses, get_all_admins
)
from bot.keyboards.keyboards import get_admin_keyboard, get_client_keyboard

class AdminStates(StatesGroup):
    waiting_for_admin_id = State()
    waiting_for_admin_action = State()
    waiting_for_bonus_user_id = State()
    waiting_for_bonus_amount = State()
    waiting_for_message_user_id = State()
    waiting_for_message_text = State()

async def admin_command(message: types.Message):
    """Обработчик команды /admin"""
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь главным админом или обычным админом
    if user_id != ADMIN_ID and not is_admin(user_id):
        await message.answer("❌ У вас нет доступа к панели администратора.")
        return
    
    keyboard = get_admin_keyboard()
    await message.answer(
        "👑 Панель администратора\n"
        "Выберите действие:",
        reply_markup=keyboard
    )

async def process_admin_user(message: types.Message, state: FSMContext):
    """Обработка кнопки управления админами"""
    if message.from_user.id != ADMIN_ID:  # Только главный админ может управлять админами
        await message.answer("❌ Только главный администратор может управлять админами.")
        return
    
    # Получаем список администраторов
    admins = get_all_admins()  
    admin_info = "\n".join([f"ID: {admin['id']}" for admin in admins])
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("❌ Отменить"))
    
    await AdminStates.waiting_for_admin_id.set()
    await message.answer(
        f"👤 Актуальные администраторы:\n{admin_info}\n\nВведите ID пользователя, которого хотите назначить/удалить админом:",
        reply_markup=keyboard
    )

async def process_admin_id(message: types.Message, state: FSMContext):
    """Обработка введенного ID для управления админами"""
    try:
        admin_id = int(message.text)
        if admin_id == ADMIN_ID:
            await message.answer("❌ Нельзя изменить права главного администратора.")
            await state.finish()
            return
        
        # Проверяем, является ли пользователь уже админом
        if is_admin(admin_id):
            # Удаляем админа
            if remove_admin(admin_id):
                await message.answer(f"✅ Пользователь {admin_id} больше не является администратором.")
            else:
                await message.answer("❌ Ошибка при удалении администратора.")
        else:
            # Добавляем нового админа
            if add_admin(admin_id, message.from_user.id):
                await message.answer(f"✅ Пользователь {admin_id} назначен администратором.")
            else:
                await message.answer("❌ Ошибка при назначении администратора.")
        
        await state.finish()
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректный ID (только цифры).")
        return

async def process_manual_bonus(message: types.Message, state: FSMContext):
    """Обработка кнопки начисления бонусов вручную"""
    if message.from_user.id != ADMIN_ID and not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой функции.")
        return
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("❌ Отменить"))
    
    await AdminStates.waiting_for_bonus_user_id.set()
    await message.answer(
        "👤 Введите ID пользователя, которому хотите начислить бонусы:",
        reply_markup=keyboard
    )

async def process_bonus_user_id(message: types.Message, state: FSMContext):
    """Обработка введенного ID пользователя для начисления бонусов"""
    if message.text.lower() == "❌ отменить":
        await state.finish()
        await message.answer("Операция отменена", reply_markup=get_admin_keyboard())
        return

    try:
        user_id = int(message.text)
        await state.update_data(bonus_user_id=user_id)
        
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("❌ Отменить"))
        
        await AdminStates.waiting_for_bonus_amount.set()
        await message.answer(
            "💫 Введите количество бонусов для начисления:",
            reply_markup=keyboard
        )
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректный ID пользователя (число).",
            reply_markup=get_admin_keyboard()
        )
        await state.finish()
        return

async def process_bonus_amount(message: types.Message, state: FSMContext):
    """Обработка введенного количества бонусов"""
    if message.text.lower() == "❌ отменить":
        await state.finish()
        await message.answer("Операция отменена", reply_markup=get_admin_keyboard())
        return

    try:
        amount = int(message.text)
        data = await state.get_data()
        
        # Логирование состояния
        print(f"DEBUG: Состояние данных: {data}")
        
        if 'bonus_user_id' not in data:
            await message.answer(
                "❌ Произошла ошибка. Пожалуйста, начните процесс начисления бонусов заново.",
                reply_markup=get_admin_keyboard()
            )
            await state.finish()
            return
            
        user_id = data['bonus_user_id']
        
        current_bonuses = get_user_bonuses(user_id)
        new_bonuses = current_bonuses + amount
        
        if new_bonuses < 0:
            await message.answer(
                "❌ Нельзя установить отрицательный баланс бонусов.",
                reply_markup=get_admin_keyboard()
            )
            await state.finish()
            return
        
        update_user_bonuses(user_id, new_bonuses)
        
        # Уведомляем админа
        bonus_word = get_bonus_word(amount)
        await message.answer(
            f"✅ Бонусы изменены!\n"
            f"👤 Пользователь: {user_id}\n"
            f"{'➕' if amount >= 0 else '➖'} Изменение: {abs(amount)} {bonus_word}\n"
            f"💫 Новый баланс: {new_bonuses} {get_bonus_word(new_bonuses)}",
            reply_markup=get_admin_keyboard()
        )
        
        # Уведомляем пользователя
        try:
            if amount > 0:
                await message.bot.send_message(
                    user_id,
                    f"✨ Вам начислено {amount} {bonus_word}!\n"
                    f"💫 Текущий баланс: {new_bonuses} {get_bonus_word(new_bonuses)}"
                )
            else:
                await message.bot.send_message(
                    user_id,
                    f"📝 С вашего счета списано {abs(amount)} {bonus_word}\n"
                    f"💫 Текущий баланс: {new_bonuses} {get_bonus_word(new_bonuses)}"
                )
        except Exception as e:
            await message.answer(
                f"⚠️ Не удалось отправить уведомление пользователю: {e}",
                reply_markup=get_admin_keyboard()
            )
        
        await state.finish()
        
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректное число бонусов.",
            reply_markup=get_admin_keyboard()
        )
        await state.finish()
        return

async def process_send_message(message: types.Message, state: FSMContext):
    """Обработка кнопки отправки сообщения"""
    if message.from_user.id != ADMIN_ID and not is_admin(message.from_user.id):
        await message.answer(
            "❌ У вас нет доступа к этой функции.",
            reply_markup=get_client_keyboard()
        )
        return
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("❌ Отменить"))
    
    await AdminStates.waiting_for_message_user_id.set()
    await message.answer(
        "👤 Введите ID пользователя, которому хотите отправить сообщение:",
        reply_markup=keyboard
    )

async def process_message_user_id(message: types.Message, state: FSMContext):
    """Обработка введенного ID для отправки сообщения"""
    if message.text.lower() == "❌ отменить":
        await state.finish()
        await message.answer("Операция отменена", reply_markup=get_admin_keyboard())
        return

    try:
        user_id = int(message.text)
        await state.update_data(message_user_id=user_id)
        
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton("❌ Отменить"))
        
        await AdminStates.waiting_for_message_text.set()
        await message.answer(
            "✍️ Введите текст сообщения:",
            reply_markup=keyboard
        )
    except ValueError:
        await message.answer(
            "❌ Пожалуйста, введите корректный ID пользователя (число).",
            reply_markup=get_admin_keyboard()
        )
        await state.finish()
        return

async def process_message_text(message: types.Message, state: FSMContext):
    """Обработка текста сообщения для отправки"""
    if message.text.lower() == "❌ отменить":
        await state.finish()
        await message.answer("Операция отменена", reply_markup=get_admin_keyboard())
        return

    data = await state.get_data()
    user_id = data.get('message_user_id')
    
    if not user_id:
        await message.answer(
            "❌ Произошла ошибка. Пожалуйста, начните процесс отправки сообщения заново.",
            reply_markup=get_admin_keyboard()
        )
        await state.finish()
        return
    
    try:
        await message.bot.send_message(user_id, message.text)
        await message.answer(
            f"✅ Сообщение успешно отправлено пользователю {user_id}",
            reply_markup=get_admin_keyboard()
        )
    except Exception as e:
        await message.answer(
            f"❌ Не удалось отправить сообщение: {str(e)}",
            reply_markup=get_admin_keyboard()
        )
    
    await state.finish()

async def cancel_admin_action(message: types.Message, state: FSMContext):
    """Отмена текущего админского действия"""
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
        await message.answer(
            "❌ Действие отменено",
            reply_markup=get_admin_keyboard()
        )

async def return_to_main_menu(message: types.Message):
    """Возврат в обычное меню"""
    await message.answer("Возвращаемся в обычное меню", reply_markup=get_client_keyboard())

def get_bonus_word(amount):
    if abs(amount) == 1:
        return "бонус"
    elif 2 <= abs(amount) <= 4:
        return "бонуса"
    else:
        return "бонусов"
