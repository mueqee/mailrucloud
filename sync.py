"""mailrucloud/sync.py
Простейшая односторонняя синхронизация: LOCAL_DIR → REMOTE_DIR.

Алгоритм:
1. Рекурсивно обходим локальную директорию.
2. Для каждого файла вычисляем remote_path.
3. Если файл отсутствует в облаке или отличается размером — загружаем.

Пока без удаления удалённых файлов и без синхронизации «из облака».
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from network import get_client
from upload import upload_file  # переиспользуем функцию


def _posix_join(*segments: str) -> str:
    """Соединяет сегменты в POSIX-путь (через "/")."""
    return "/".join(s.strip("/") for s in segments if s)


def sync_directories(local_dir: str, remote_dir: str = "/") -> None:
    client = get_client()

    local_dir_path = Path(local_dir).expanduser().resolve()
    for root, _dirs, files in os.walk(local_dir_path):
        root_path = Path(root)
        rel_root = root_path.relative_to(local_dir_path)
        for fname in files:
            local_path = root_path / fname
            rel_path = rel_root / fname if rel_root != Path('.') else Path(fname)
            remote_path = _posix_join(remote_dir, str(rel_path).replace(os.sep, '/'))

            # Проверяем наличие файла в облаке
            needs_upload = False
            try:
                if not client.check(remote_path):  # type: ignore[arg-type]
                    needs_upload = True
                else:
                    info: dict[str, Any] = client.info(remote_path)  # type: ignore[arg-type]
                    remote_size = int(info.get('size', -1))
                    local_size = local_path.stat().st_size
                    if remote_size != local_size:
                        needs_upload = True
            except Exception:
                needs_upload = True  # если вдруг ошибка проверки — перезаписываем

            if needs_upload:
                print(f"→ upload {local_path} → {remote_path}")
                # ensure parent dir exists
                parent_remote = "/" + "/".join(remote_path.strip('/').split('/')[:-1])
                if parent_remote and not client.check(parent_remote):  # type: ignore[arg-type]
                    client.mkdir(parent_remote)  # type: ignore[arg-type]
                upload_file(str(local_path), remote_path) 