# Mailru Cloud CLI

[![CI](https://github.com/mueqee/mailrucloud/actions/workflows/ci.yml/badge.svg)](https://github.com/mueqee/mailrucloud/actions/workflows/ci.yml)
[![Publish](https://github.com/mueqee/mailrucloud/actions/workflows/publish.yml/badge.svg)](https://github.com/mueqee/mailrucloud/actions/workflows/publish.yml)
[![PyPI](https://img.shields.io/pypi/v/mailru-cloud-cli.svg)](https://pypi.org/project/mailru-cloud-cli/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> Неофициальный Python-CLI [Mail.ru Облака](https://cloud.mail.ru) клиент для майл ру, работающий через WebDAV

`mailrucloud` позволяет управлять файлами из терминала: загружать, скачивать, синхронизировать каталоги, получать информацию о файлах и многое другое. Проект вдохновлён [gdrive](https://github.com/prasmussen/gdrive) и стремится предоставить такой же простой UX, но для Mail.ru Cloud.

---

## 📑 Содержание

1. [Возможности](#-возможности)
2. [Установка](#-установка)
3. [Быстрый старт](#-быстрый-старт)
4. [Список команд](#-список-команд)
5. [Примеры использования](#-примеры-использования)
6. [Синхронизация](#-синхронизация)
7. [Roadmap](#-roadmap)
8. [Сборка из исходников](#-сборка-из-исходников)
9. [Contributing](#-contributing)
10. [Лицензия](#-лицензия)

---

## 🚀 Возможности

* Авторизация с использованием **паролей приложений** Mail.ru (2FA friendly)
* Просмотр содержимого облака (`ls`)
* Загрузка и скачивание файлов (`upload`, `download`)
* Одно/двухсторонняя синхронизация каталогов (`sync push / pull / both`)
* Удаление, перемещение, переименование файлов / папок (`rm`, `mv`)
* Получение подробной информации о файле (`info`)
* Чистый вывод в CLI и дружелюбные emoji-индикаторы
* 100 % тестовое покрытие fast-unit сценариев, CI на GitHub Actions
* Рекурсивная загрузка директорий с автоматическим созданием всех вложенных папок в облаке (sync push)

## 📦 Установка

> Требования: Python ≥ 3.10

### Вариант 1: PyPI (стабильная версия)
```bash
pip install mailru-cloud-cli
```
> Если видите ошибку "externally-managed-environment", используйте виртуальное окружение:
```bash
python3 -m venv .venv --upgrade-deps
source .venv/bin/activate
```
> Список команд
```
mailrucloud --help
```
### Вариант 2: TestPyPI (текущие бета-релизы)
```bash
python -m pip install --upgrade \
  -i https://test.pypi.org/simple \
  --extra-index-url https://pypi.org/simple \
  mailru-cloud-cli==1.4.0
```

### Вариант 3: Из исходников (рекомендуется для разработки)
```bash
git clone https://github.com/mueqee/mailrucloud.git
cd mailrucloud
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py --help
```

## ⚡️ Быстрый старт

```bash
# 1. Авторизация (email + пароль приложения Mail.ru)
mailrucloud login

# 2. Посмотреть содержимое корня
mailrucloud ls

# 3. Загрузить файл
mailrucloud upload ./photo.jpg /Photos/2024/

# 4. Скачать файл
mailrucloud download /Photos/2024/photo.jpg ./
```

При первой авторизации токен сохраняется в `~/.mailru_token.json`.

## 📚 Список команд

| Команда | Описание |
|---------|----------|
| `login` | Войти в облако Mail.ru |
| `ls [REMOTE_DIR]` | Список файлов/папок (default `/`) |
| `upload <LOCAL_PATH> [--remote-path PATH]` | Загрузка файла |
| `download <REMOTE_PATH> [LOCAL_PATH]` | Скачивание файла |
| `sync [OPTIONS] <LOCAL_DIR> <REMOTE_DIR>` | Синхронизация каталогов |
| `rm <REMOTE_PATH>` | Удаление файла/папки |
| `mv <SRC> <DST>` | Переименование/перемещение |
| `info <REMOTE_PATH>` | Подробная информация о файле |

Все команды поддерживают флаг `--help` для подробной справки.

## 🔍 Примеры использования

```bash
# Рекурсивный вывод содержимого каталога
mailrucloud ls /Documents

# Односторонний бэкап (push)
mailrucloud sync ~/Projects /Backup --direction push

# Отобразить размер и дату изменения файла
mailrucloud info /Backup/report.pdf

# Удалить файл
mailrucloud rm /Backup/old.zip
```

## 🔄 Синхронизация каталогов

`sync` сопоставляет структуры директорий, копируя недостающие или изменённые файлы.
Удаление в режиме `both` пока **не** отражается (безопасный режим). Алгоритм основан на сравнении хэшей и временных меток.

```bash
# Двусторонняя синхронизация (значение по умолчанию)
mailrucloud sync ~/Notes /CloudNotes

# Только из облака → локально
mailrucloud sync ~/Notes /CloudNotes -d pull

# Только локально → облако
mailrucloud sync ~/Notes /CloudNotes --direction push

# Быстрая многопоточная загрузка (8 потоков)
mailrucloud sync ~/Notes /CloudNotes --direction push --threads 8

# Загрузка только новых файлов (без проверки размера)
mailrucloud sync ~/Notes /CloudNotes --direction push --only-new

# Комбинированный режим для максимальной скорости
mailrucloud sync ~/Notes /CloudNotes --direction push --threads 8 --only-new
```

## 🛣 Roadmap

- [x] Публикация стабильной версии в основное PyPI 
- [x] Рекурсивное создание директорий при загрузке (sync push)
- [x] Многопоточная загрузка файлов для ускорения синхронизации
- [x] Улучшенный прогресс-бар с процентами, счётчиком файлов и оставшимся временем
- [ ] Поддержка удаления при двусторонней синхронизации
- [ ] Проверка целостности (md5) после загрузки/скачивания
- [ ] Параллельная (мультитред) загрузка/скачивание больших файлов
- [ ] Интерактивный TUI-режим (rich-console)
- [ ] Trusted Publishing для TestPyPI и PyPI (без API-токенов)
- [ ] Кроссплатформенная сборка и тестирование (Windows/macOS)
- [ ] Вывод прогресса операций через `rich.progress`
- [ ] Docker-образ `mailrucloud` для быстрого использования
- [ ] Генератор автокомплита Bash/Zsh/Fish для CLI
- [ ] Поддержка шифрования токена учётных данных

## 🛠 Сборка из исходников

Проект использует **PEP 517** (setuptools). Локальная сборка:
```bash
python -m pip install --upgrade build
python -m build
```
Исходники пакуются в `dist/`.

## 🤝 Contributing

Pull requests приветствуются! Перед отправкой:
1. Создайте issue или обсудите идею в дискуссии.
2. Убедитесь, что `pytest -v` проходит локально.
3. Соблюдайте Conventional Commits на русском.
4. Запустите `flake8` / `mypy` при необходимости.

## 📝 Лицензия

Пакет распространяется под лицензией **MIT**. Полный текст — в файле [LICENSE](LICENSE).
