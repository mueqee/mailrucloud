import requests
from auth import load_token

def list_files(path="/"):
    token_data = load_token()
    if not token_data:
        print("Токен не найден. Выполните вход через 'login'.")
        return []

    access_token = token_data.get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "home": "true",
        "page": 1,
        "limit": 100
    }

    url = "https://cloud.mail.ru/api/v2/folder"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        items = response.json().get("body", {}).get("list", [])
        return [item["name"] for item in items]
    else:
        print("Ошибка получения списка файлов:", response.text)
        return []