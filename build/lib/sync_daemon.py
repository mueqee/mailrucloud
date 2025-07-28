"""Фоновый демон синхронизации Mailru Cloud.

Запускается в отдельном процессе командой `mailrucloud start`.
Каждую минуту синхронизирует каталог `~/Mail.Cloud` с корнем облака `/`.
"""
from pathlib import Path
import signal
import sys
import time
import os

from sync import sync_directories

RUNNING = True


def _signal_handler(signum, frame):
    global RUNNING
    RUNNING = False


signal.signal(signal.SIGTERM, _signal_handler)
# SIGINT полезен при отладке через Ctrl+C, но в проде процесс будет в фоне.
signal.signal(signal.SIGINT, _signal_handler)

LOCAL_DIR = str(Path.home() / "Mail.Cloud")
REMOTE_DIR = "/"
INTERVAL_SEC = 60  # частота синхронизации
PID_FILE = str(Path.home() / ".mailrucloud-daemon.pid")


if __name__ == "__main__":
    Path(LOCAL_DIR).mkdir(exist_ok=True)
    # Записываем PID в файл
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    try:
        while RUNNING:
            try:
                sync_directories(LOCAL_DIR, REMOTE_DIR, direction="both")
            except Exception as exc:
                # Логируем ошибку в stderr, но продолжаем работу
                print(f"[sync-daemon] Ошибка синхронизации: {exc}", file=sys.stderr, flush=True)
            time.sleep(INTERVAL_SEC)
    finally:
        # Удаляем PID-файл при завершении
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE) 