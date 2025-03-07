from ..config.config import USERS_FILE

def load_users():
    try:
        with open(USERS_FILE, 'r') as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def save_user(user_id):
    with open(USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")

def get_bonus_word(count):
    if count % 10 == 1 and count % 100 != 11:
        return "бонус"
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return "бонуса"
    else:
        return "бонусов"
