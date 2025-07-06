from network import get_client


def download_file(remote_path: str, local_path: str) -> bool:
    """Скачивает файл `remote_path` из облака на локальный диск.`"""
    client = get_client()
    try:
        client.download_sync(remote_path=remote_path, local_path=local_path)
        print(f"Файл сохранён в: {local_path}")
        return True
    except Exception as exc:
        print(f"Ошибка скачивания: {exc}")
        return False