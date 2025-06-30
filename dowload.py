import requests
from auth import load_token, refresh_token

DOWNLOAD_LINK_URL = "https://cloud.mail.ru/api/v2/file/download"

def _get_with_refresh(url, params=None, stream=False):
    token_data = load_token()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"} if token_data else {}
    response = requests.get(url, headers=headers, params=params, stream=stream)
    if response.status_code == 401:
        print("[DEBUG] Токен истёк, обновляем...")
        if refresh_token():
            token_data = load_token()
            headers["Authorization"] = f"Bearer {token_data['access_token']}"
            response = requests.get(url, headers=headers, params=params, stream=stream)
    return response

def get_download_url(remote_path):
    token_data = load_token()
    if not token_data:
        print("Токен не найден. Выполните вход через 'login'.")
        return None

    headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }

    params = {
        "home": "true",
        "weblink": "false",
        "cloud_file": remote_path
    }

    response = requests.get(DOWNLOAD_LINK_URL, headers=headers, params=params)
    if response.status_code == 200:
        body = response.json().get("body", {})
        return body.get("url")
    else:
        print("Ошибка получения ссылки скачивания:", response.text)
        return None

def download_file(remote_path, local_path):
    url = get_download_url(remote_path)
    if not url:
        return False

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Файл сохранён в: {local_path}")
        return True
    else:
        print("Ошибка скачивания:", response.text)
        return False
