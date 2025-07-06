"""mailrucloud/sync.py
Синхронизация директорий через WebDAV.

Поддерживаются три направления:
• "push"  — только отправка локальных файлов в облако (как было раньше).
• "pull"  — только получение новых/изменённых файлов из облака.
• "both"  — двусторонний обмен (по умолчанию).

Удаление файлов пока *не* реализовано: синхронизация работает по принципу
«кто новее/отсутствует — тот копируется», конфликты разрешаются по размеру.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from network import get_client
from upload import upload_file  # переиспользуем функцию
from download import download_file


def _posix_join(*segments: str) -> str:
    """Соединяет сегменты в POSIX-путь (через "/")."""
    return "/".join(s.strip("/") for s in segments if s)


def sync_directories(local_dir: str, remote_dir: str = "/", direction: str = "both") -> None:
    """Синхронизация содержимого *local_dir* и *remote_dir*.

    Parameters
    ----------
    local_dir : str
        Путь к локальной директории.
    remote_dir : str, optional
        Директория в облаке (по умолчанию корень «/»).
    direction : {"push", "pull", "both"}
        Что делать:
        - "push": только загрузка локальных изменений в облако.
        - "pull": только выгрузка облачных изменений локально.
        - "both": двусторонняя синхронизация.
    """

    if direction not in {"push", "pull", "both"}:
        raise ValueError("direction должен быть 'push', 'pull' или 'both'")

    client = get_client()

    local_dir_path = Path(local_dir).expanduser().resolve()

    # --- PUSH: локальное → облако -------------------------------------------------
    if direction in {"push", "both"}:
        for root, _dirs, files in os.walk(local_dir_path):
            root_path = Path(root)
            rel_root = root_path.relative_to(local_dir_path)
            for fname in files:
                local_path = root_path / fname
                rel_path = rel_root / fname if rel_root != Path('.') else Path(fname)
                remote_path = _posix_join(remote_dir, str(rel_path).replace(os.sep, '/'))

                # Проверяем необходимость загрузки
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
                    needs_upload = True

                if needs_upload:
                    print(f"→ upload {local_path} → {remote_path}")
                    # ensure parent dir exists
                    parent_remote = "/" + "/".join(remote_path.strip('/').split('/')[:-1])
                    if parent_remote and not client.check(parent_remote):  # type: ignore[arg-type]
                        client.mkdir(parent_remote)  # type: ignore[arg-type]
                    upload_file(str(local_path), remote_path)

    # --- PULL: облако → локальная -------------------------------------------------
    if direction in {"pull", "both"}:

        def _walk_remote(dir_path: str):
            for item in client.list(dir_path):  # type: ignore[arg-type]
                if item in {".", ".."}:
                    continue
                remote_item_path = _posix_join(dir_path, item)
                try:
                    if client.is_dir(remote_item_path):  # type: ignore[arg-type]
                        yield from _walk_remote(remote_item_path)
                    else:
                        yield remote_item_path
                except Exception:
                    # Если не удаётся определить тип — пропускаем
                    continue

        for remote_file in _walk_remote(remote_dir):
            # Получаем относительный путь от remote_dir
            rel_remote = remote_file[len(remote_dir):] if remote_dir != "/" else remote_file.lstrip("/")
            local_path = local_dir_path / rel_remote

            # Нужно ли скачивать?
            needs_download = False
            try:
                if not local_path.exists():
                    needs_download = True
                else:
                    info: dict[str, Any] = client.info(remote_file)  # type: ignore[arg-type]
                    remote_size = int(info.get('size', -1))
                    local_size = local_path.stat().st_size
                    if remote_size != local_size:
                        needs_download = True
            except Exception:
                needs_download = True

            if needs_download:
                print(f"← download {remote_file} → {local_path}")
                local_path.parent.mkdir(parents=True, exist_ok=True)
                download_file(remote_file, str(local_path)) 