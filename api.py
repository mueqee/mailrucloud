import requests
from auth import load_token
from auth import refresh_token

def _request_with_refresh(method, url, **kwargs):
    token_data = load_token()
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {token_data['access_token']}" if token_data else ""
    response = requests.request(method, url, headers=headers, **kwargs)
    if response.status_code == 401:
        # Попытка обновить токен
        print("[DEBUG] Токен истёк, обновляем...")
        if refresh_token():
            token_data = load_token()
            headers["Authorization"] = f"Bearer {token_data['access_token']}"
            response = requests.request(method, url, headers=headers, **kwargs)
    return response

def list_files(path: str = "/") -> list:
    token_data = load_token()
    if not token_data:
        print("Токен не найден. Выполните вход через 'login'.")
        return []

    access_token = token_data.get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    params = {
        "folder": path,
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