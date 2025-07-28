from network import get_client


def list_files(path: str = "/") -> list[str]:
    """Возвращает список файлов/папок в указанной директории.
    Работает через WebDAV.
    """
    client = get_client()
    try:
        return client.list(path)  # type: ignore[arg-type]
    except Exception as exc:
        print(f"Ошибка при получении списка файлов: {exc}")
    return [] 


# --- Дополнительные операции ---------------------------------------------------


def delete_file(remote_path: str) -> bool:
    """Удаляет файл или папку *remote_path* в облаке."""
    client = get_client()
    try:
        client.clean(remote_path)  # type: ignore[arg-type]
        return True
    except Exception as exc:
        print(f"Ошибка удаления: {exc}")
        return False


def move_file(src_path: str, dst_path: str) -> bool:
    """Переименовывает/перемещает ресурс в облаке."""
    client = get_client()
    try:
        client.move(src_path, dst_path)  # type: ignore[arg-type]
        return True
    except Exception as exc:
        print(f"Ошибка перемещения: {exc}")
        return False


def file_info(remote_path: str) -> dict:
    """Возвращает словарь информации о файле (size, modified и т.п.)."""
    client = get_client()
    try:
        return client.info(remote_path)  # type: ignore[arg-type]
    except Exception as exc:
        print(f"Ошибка info: {exc}")
        return {} 