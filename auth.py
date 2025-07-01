import requests
import json
import os
from config import load_config
from typing import Optional

TOKEN_FILE = ".token.json"
API_URL = "https://o2.mail.ru/token"
CLIENT_ID = "cloud-win"

def login(username, password):
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": username,
        "password": password
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(API_URL, data=data, headers=headers)

    response = requests.post(API_URL, data=data, headers=headers)

    if response.status_code == 200:
        tokens = response.json()
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f)
        print("Успешная авторизация. Токен сохранён.")
        return True
    else:
        print("Ошибка авторизации:", response.text)
        return False

def load_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return json.load(f)
    return None

def refresh_token():
    config = load_config()
    email = config.get("email")
    password = config.get("password")
    if not email or not password:
        raise RuntimeError("Не удалось обновить токен: в конфиге отсутствуют email или password")
    print(f"[DEBUG] Обновление токена для {email}...")
    return login(email, password)

def save_token(data: dict):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[DEBUG] Сохранили токен: {data}")


def get_token() -> Optional[str]:
    try:
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
        print(f"[DEBUG] Загрузили токен из файла: {data}")
        return data.get("access_token")
    except FileNotFoundError:
        print("[DEBUG] Файл токена не найден.")
        return None
