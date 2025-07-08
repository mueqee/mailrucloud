# mailrucloud/auth.py
"""Модуль авторизации для WebDAV-доступа к Облаку Mail.ru.
Схема проста: сохраняем в файл email и *пароль для внешнего приложения*.
Никаких сетевых запросов при логине не требуется – WebDAV обрабатывает
Basic-авторизацию самостоятельно.
"""

import json
from pathlib import Path
from typing import Optional

CRED_FILE = Path.home() / ".mailru_token.json"


def login(username: str, app_password: str) -> bool:
    """Сохраняет учётные данные в файл.

    Parameters
    ----------
    username : str
        Полный e-mail пользователя (например, `user@mail.ru`).
    app_password : str
        Пароль для внешнего приложения, созданный в настройках безопасности
        Mail.ru. *Не* обычный пароль от почты!
    """
    if "@" not in username:
        print("❌ Введите полный e-mail, например user@mail.ru")
        return False

    data = {"email": username, "password": app_password}
    try:
        CRED_FILE.write_text(json.dumps(data))
        print(f"✅ Данные сохранены в {CRED_FILE}")
        return True
    except OSError as exc:
        print(f"❌ Не удалось сохранить файл учётных данных: {exc}")
        return False


def load_credentials() -> Optional[dict]:
    """Читает файл учётных данных и возвращает словарь с ключами
    `email` и `password`. Если файл отсутствует – ``None``.
    """
    if not CRED_FILE.exists():
        return None
    try:
        return json.loads(CRED_FILE.read_text())
    except (OSError, json.JSONDecodeError):
    return None