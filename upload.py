import requests
import hashlib
import os
from auth import load_token, refresh_token

UPLOAD_LINK_URL = "https://cloud.mail.ru/api/v2/file/add"

def _post_with_refresh(url, params=None, data=None, files=None, stream=False):
    token_data = load_token()
    headers = {"Authorization": f"Bearer {token_data['access_token']}"} if token_data else {}
    response = requests.post(url, headers=headers, params=params, data=data, files=files, stream=stream)
    if response.status_code == 401:
        print("[DEBUG] Токен истёк, обновляем...")
        if refresh_token():
            token_data = load_token()
            headers["Authorization"] = f"Bearer {token_data['access_token']}"
            response = requests.post(url, headers=headers, params=params, data=data, files=files, stream=stream)
    return response

def get_upload_url(filename, filesize):
    token_data = load_token()
    if not token_data:
        print("Токен не найден. Выполните вход через 'login'.")
        return None

    headers = {
        "Authorization": f"Bearer {token_data['access_token']}"
    }

    filehash = hashlib.md5((filename + str(filesize)).encode()).hexdigest()

    params = {
        "home": "true",
        "conflict": "rename",
        "hash": filehash,
        "size": filesize,
        "name": os.path.basename(filename)
    }

    response = _post_with_refresh(UPLOAD_LINK_URL, params=params)
    if response.status_code == 200:
        body = response.json().get("body", {})
        return body.get("upload_url"), body.get("cloud_path")
    else:
        print("Ошибка получения ссылки загрузки:", response.text)
        return None, None

def upload_file(local_path):
    if not os.path.exists(local_path):
        print("Файл не найден:", local_path)
        return False

    filesize = os.path.getsize(local_path)
    upload_url, remote_path = get_upload_url(local_path, filesize)
    if not upload_url:
        return False

    with open(local_path, "rb") as f:
        response = requests.put(upload_url, data=f)

    if response.status_code == 200 or response.status_code == 201:
        print(f"Файл успешно загружен в: {remote_path}")
        return True
    else:
        print("Ошибка при загрузке:", response.text)
        return False
