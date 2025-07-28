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
from rich.progress import Progress
from concurrent.futures import ThreadPoolExecutor, as_completed


def _posix_join(*segments: str) -> str:
    """Соединяет сегменты в POSIX-путь (через "/")."""
    return "/".join(s.strip("/") for s in segments if s)


def ensure_remote_dirs(client, remote_path):
    """Рекурсивно создаёт все родительские директории в облаке."""
    parts = remote_path.strip('/').split('/')
    for i in range(1, len(parts)+1):
        subdir = '/' + '/'.join(parts[:i])
        if not client.check(subdir):
            client.mkdir(subdir)


def sync_directories(local_dir: str, remote_dir: str = "/", direction: str = "both", threads: int = 4, only_new: bool = False) -> None:
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
        # Собираем список всех файлов для загрузки
        files_to_upload = []
        for root, _dirs, files in os.walk(local_dir_path):
            root_path = Path(root)
            rel_root = root_path.relative_to(local_dir_path)
            for fname in files:
                local_path = root_path / fname
                rel_path = rel_root / fname if rel_root != Path('.') else Path(fname)
                remote_path = _posix_join(remote_dir, str(rel_path).replace(os.sep, '/'))

                needs_upload = False
                try:
                    if not client.check(remote_path):
                        needs_upload = True
                    elif not only_new:
                        remote_info: dict[str, Any] = client.info(remote_path)
                        remote_size = int(remote_info.get('size', -1))
                        local_size = local_path.stat().st_size
                        if remote_size != local_size:
                            needs_upload = True
                except Exception:
                    needs_upload = True

                if needs_upload:
                    files_to_upload.append((local_path, remote_path))

        def upload_task(local_path, remote_path):
            import time
            start = time.time()
            parent_remote = "/" + "/".join(remote_path.strip('/').split('/')[:-1])
            if parent_remote:
                ensure_remote_dirs(client, parent_remote)
            
            # Получаем размер файла для расчёта скорости
            file_size = local_path.stat().st_size
            upload_file(str(local_path), remote_path)
            end = time.time()
            duration = end - start
            speed = file_size / duration if duration > 0 else 0
            speed_mb = speed / (1024 * 1024)  # МБ/с
            
            return local_path, remote_path, duration, file_size, speed_mb

        if len(files_to_upload) > 0:
            with Progress(
                "[progress.description]{task.description}",
                "[progress.percentage]{task.percentage:>3.0f}%",
                "({task.completed}/{task.total} файлов)",
                "[red]ETA: {task.time_remaining}",
                "[cyan]Скорость: {task.speed:.1f} МБ/с",
                transient=False
            ) as progress:
                task = progress.add_task("Загрузка файлов...", total=len(files_to_upload))
                total_size = 0
                total_duration = 0
                
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = [executor.submit(upload_task, lp, rp) for lp, rp in files_to_upload]
                    for future in as_completed(futures):
                        local_path, remote_path, duration, file_size, speed_mb = future.result()
                        total_size += file_size
                        total_duration += duration
                        avg_speed = (total_size / (1024 * 1024)) / total_duration if total_duration > 0 else 0
                        
                        progress.update(task, advance=1, speed=avg_speed, 
                                      description=f"[green]✓ {local_path.name}")
                        print(f"[✓] {local_path} → {remote_path} ({duration:.2f} сек, {speed_mb:.1f} МБ/с)")
        else:
            print("Нет файлов для загрузки")

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