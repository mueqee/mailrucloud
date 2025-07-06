# mailru-cloud (Python CLI)

Неофициальный CLI-клиент для Mail.ru Cloud, написанный на Python.

## Установка

```bash
git clone https://github.com/youruser/mailru-cloud-python.git
cd mailru-cloud-python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Команды

- `login`: Войти в облако
- `ls`: Показать список файлов/папок
- `upload <LOCAL_PATH>`: Загрузить файл в облако
- `download`: Скачать файл (пример ниже)

### Авторизация и пароли

При первом запуске используйте команду:

`python main.py login`

CLI запросит ваш email и пароль от Mail.ru.

> ⚠️ Если у вас включена двухфакторная аутентификация (2FA), необходимо использовать пароль приложения.

#### Как получить пароль приложения

   1. Откройте: **https://account.mail.ru/user/2-step-auth/**

   2. Перейдите в раздел «Пароли приложений»

   3. Создайте новый пароль (например, MailruCloud CLI)

   4. Используйте этот пароль вместо основного при входе через login

#### Поддерживаемые почты

Поддерживаются только аккаунты Mail.ru:

   - @mail.ru
   - @inbox.ru
   - @bk.ru
   - @list.ru

    🛑 Аккаунты с доменом @vk.com не поддерживаются, даже если вы можете войти на сайт cloud.mail.ru вручную.


## Быстрый тест WebDAV

```bash
# Список содержимого
python main.py ls

# Загрузка файла
echo "hello" > /tmp/hello.txt
python main.py upload /tmp/hello.txt

# Скачивание файла
python - <<'PY'
from download import download_file
download_file('/hello.txt', '/tmp/hello_from_cloud.txt')
PY

diff /tmp/hello.txt /tmp/hello_from_cloud.txt  # должно быть пусто
```

При выполнении `python main.py login` создаётся файл `~/.mailru_token.json`
