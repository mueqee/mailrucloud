import os
from pathlib import Path

from network import get_client


def upload_file(local_path: str, remote_dir: str = "/") -> bool:
    """Загружает файл `local_path` в облако в папку `remote_dir`.

    Согласно спецификации WebDAV, если файл уже существует, он будет
    перезаписан. При необходимости можно beforehand проверить наличие
    через `client.check`.
    """
    if not os.path.exists(local_path):
        print("Файл не найден:", local_path)
        return False

    client = get_client()
    filename = Path(local_path).name
    remote_path = os.path.join(remote_dir, filename)

    try:
        client.upload_sync(remote_path=remote_path, local_path=local_path)
        return True
    except Exception as exc:
        print(f"Ошибка при загрузке файла: {exc}")
        return False