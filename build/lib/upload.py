import os
from pathlib import Path

from network import get_client


def upload_file(local_path: str, remote_path: str | None = None) -> bool:
    """Загружает файл `local_path` в облако.

    Если `remote_path` не указан, файл сохраняется в корне облака под тем же
    именем.  При конфликтах WebDAV перезаписывает существующий файл.
    """
    if not os.path.exists(local_path):
        print("Файл не найден:", local_path)
        return False

    if remote_path is None:
        remote_path = "/" + Path(local_path).name

    client = get_client()

    try:
        client.upload_sync(remote_path=remote_path, local_path=local_path)
        return True
    except Exception as exc:
        print(f"Ошибка при загрузке файла: {exc}")
        return False