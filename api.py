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