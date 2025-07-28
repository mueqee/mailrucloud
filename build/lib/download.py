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
        # Основной путь: штатная реализация библиотеки
        client.download_sync(remote_path=remote_path, local_path=str(local_path))
        print(f"Файл сохранён в: {local_path}")
        return True
    except Exception as exc:
        # Для некоторых (особенно пустых или очень маленьких) файлов у облака
        # отсутствует заголовок ``Content-Length``.  Штатная реализация
        # `webdavclient3` в таком случае падает с KeyError.  Пытаемся обойти
        # проблему: скачиваем файл «вручную» тем же клиентом, но напрямую через
        # низкоуровневый `execute_request`, игнорируя прогресс.

        if "content-length" in str(exc).lower():
            try:
                from webdav3.urn import Urn  # импорт здесь, чтобы избежать лишней зависимости при обычной работе

                # Получаем поток ответа на GET.
                response = client.execute_request(action="download", path=Urn(remote_path).quote())

                # Стримингом пишем в файл.
                with open(local_path, "wb") as fp:
                    for chunk in response.iter_content(chunk_size=client.chunk_size):
                        if chunk:  # пропускаем keep-alive
                            fp.write(chunk)

                print(f"Файл сохранён в: {local_path} (fallback)")
                return True
            except Exception as exc_fallback:
                print(f"Ошибка скачивания (fallback): {exc_fallback}")
                return False

        # Иная ошибка – просто выводим и возвращаем False
        print(f"Ошибка скачивания: {exc}")
        return False