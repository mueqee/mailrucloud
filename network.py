"""mailrucloud/network.py
Поставщик WebDAV-клиента, настроенного с учётными данными из auth.py.
Использует библиотеку `webdavclient3`.
"""

from typing import Optional
from webdav3.client import Client  # type: ignore
from auth import load_credentials


_cached_client: Optional[Client] = None  # Singleton, чтобы не создавать несколько раз


def get_client() -> Client:
    """Возвращает настроенный экземпляр WebDAV-клиента.

    Raises
    ------
    RuntimeError
        Если учётные данные отсутствуют.
    """
    global _cached_client
    if _cached_client is not None:
        return _cached_client

    creds = load_credentials()
    if creds is None:
        raise RuntimeError("Учётные данные не найдены. Выполните команду login сначала.")

    options = {
        "webdav_hostname": "https://webdav.cloud.mail.ru",
        "webdav_login": creds["email"],
        "webdav_password": creds["password"],
    }
    _cached_client = Client(options)
    return _cached_client