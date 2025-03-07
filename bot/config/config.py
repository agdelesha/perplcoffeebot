import os

# Получаем абсолютный путь к директории бота
BOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BOT_DIR)

API_TOKEN = '7249417951:AAEkukoKpHGgeI8bEIfO6QIyZvHXtn_ExOw'
BARISTA_CHAT_ID = '-1002207660740'
GOROHOVAYA_CHAT_ID = '-4667380623'
ADMIN_ID = 906888481
USERS_FILE = os.path.join(BOT_DIR, 'resources', 'users.txt')
BONUSES_FOR_DRINK = 6

# Database configuration
DATABASE_FILE = os.path.join(BOT_DIR, 'resources', 'coffee_shop.db')

# Resource files
WELCOME_IMAGE = os.path.join(BOT_DIR, 'resources', 'XXXL-3.webp')
ABOUT_IMAGE = os.path.join(BOT_DIR, 'resources', 'xlxl.webp')
MENU_IMAGES = [
    os.path.join(BOT_DIR, 'resources', 'menu1.jpg'),
    os.path.join(BOT_DIR, 'resources', 'menu2.jpg'),
    os.path.join(BOT_DIR, 'resources', 'menu3.jpg')
]
