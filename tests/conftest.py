"""Общая конфигурация pytest для тестов проекта.
Добавляет корень репозитория в `sys.path`, чтобы модули (`api`, `cli` и др.)
импортировались корректно без установки пакета.
"""

from pathlib import Path
import sys
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --- Автопатч get_client для всех модулей --------------------------------------

import importlib
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def _mock_global_client(monkeypatch, request):  # noqa: PT004
    """Мокаем WebDAV-клиент во всех тестах, кроме помеченных @pytest.mark.slow."""

    if request.node.get_closest_marker("slow"):
        # Интеграционные slow-тесты используют реальный клиент
        yield None
        return

    dummy = MagicMock(name="DummyClient")

    # Базовые заглушки
    dummy.list.side_effect = lambda path="/": []
    dummy.clean.side_effect = lambda *a, **k: None
    dummy.move.side_effect = lambda *a, **k: None
    dummy.info.side_effect = lambda path: {}
    dummy.upload_sync.side_effect = lambda *a, **k: None
    dummy.download_sync.side_effect = lambda *a, **k: None

    monkeypatch.setattr("network.get_client", lambda: dummy)
    for mod_name in ("api", "cli", "upload", "download", "sync"):
        mod = sys.modules.get(mod_name)
        if mod is not None and hasattr(mod, "get_client"):
            monkeypatch.setattr(mod, "get_client", lambda: dummy, raising=False)

    yield dummy 