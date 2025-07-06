"""Integration tests for upload & download using sample files.

Prerequisites:
- В домашней директории пользователя должен существовать файл `~/.mailru_token.json`
  с корректными учётными данными (создаётся через `python main.py login`).
- В корне проекта присутствуют три тестовых файла:
  * test_empty.txt  (0  КБ)
  * test_small.txt  (≈1.3 КБ)
  * test_image.jpg  (≈1.5 МБ)

Тесты:
1. upload_file работает и возвращает True.
2. Файл появляется в списке client.list().
3. download_file возвращает тот же байтовый контент.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import pytest

# Добавляем корневой каталог проекта в sys.path, чтобы импорты работали
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api import list_files
from upload import upload_file
from download import download_file

SAMPLES = [
    ("test_empty.txt", "/test_empty.txt"),
    ("test_small.txt", "/test_small.txt"),
    ("test_image.jpg", "/test_image.jpg"),
]


@pytest.mark.parametrize("local_name, remote_path", SAMPLES)
def test_upload_and_download(local_name: str, remote_path: str, tmp_path: Path) -> None:
    local_path = Path(__file__).parent / local_name
    assert local_path.exists(), f"Sample file {local_name} missing"

    # --- upload ---
    assert upload_file(str(local_path), remote_path), "upload failed"

    # --- check appears in list ---
    files = list_files("/")
    assert Path(remote_path).name in files

    # --- download ---
    local_copy = tmp_path / local_name
    assert download_file(remote_path, str(local_copy)), "download failed"

    assert local_copy.exists()

    # --- compare hashes ---
    def md5(p: Path) -> str:
        h = hashlib.md5()
        h.update(p.read_bytes())
        return h.hexdigest()

    assert md5(local_copy) == md5(local_path), "file contents differ after roundtrip" 