import requests
import json
import os

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