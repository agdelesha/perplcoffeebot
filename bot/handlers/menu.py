from aiogram import types
from aiogram.types import InputFile, MediaGroup
from ..config.config import MENU_IMAGES

async def send_menu(message: types.Message):
    media = MediaGroup()
    for image_path in MENU_IMAGES:
        media.attach_photo(InputFile(image_path))
    
    await message.bot.send_media_group(message.chat.id, media=media)
