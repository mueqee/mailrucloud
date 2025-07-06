from pathlib import Path
from network import get_client


def download_file(remote_path: str, local_path: str | None = None) -> bool:
    """Скачивает файл `remote_path` из облака.

    Параметры
    ---------
    remote_path : str
        Путь к файлу в облаке (например, "/docs/report.pdf").
    local_path : str | None
        Куда сохранить файл на диске. Если *None*, используется имя файла
        из `remote_path` и текущий каталог.
    """
    if local_path is None:
        local_path = Path(remote_path).name

    client = get_client()
    try:
        client.download_sync(remote_path=remote_path, local_path=str(local_path))
        print(f"Файл сохранён в: {local_path}")
        return True
    except Exception as exc:
        print(f"Ошибка скачивания: {exc}")
        return False