import click
from auth import login
from api import list_files, delete_file, move_file, file_info
from upload import upload_file
from download import download_file
from sync import sync_directories

@click.group()
def cli():
    """mailru-cloud: неофициальный Python-клиент для Mail.ru Облака"""
    pass

@cli.command()
@click.option("--username", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
def login_cmd(username, password):
    """Авторизация в Mail.ru Cloud"""
    success = login(username, password)
    if success:
        click.echo("✅ Успешная авторизация.")
    else:
        click.echo("❌ Ошибка авторизации.")


@cli.command()
@click.argument('remote_dir', default='/', required=False)
def ls(remote_dir):
    """Показать содержимое каталога в облаке (по умолчанию «/»)."""
    files = list_files(remote_dir)
    for f in files:
        click.echo(f)


@cli.command()
@click.argument('local_path', type=click.Path(exists=True))
@click.option('--remote-path', default=None, help='Целевой путь в облаке (по умолчанию /<имя_файла>)')
def upload(local_path, remote_path):
    """
    Загрузка одного файла в облако.

    LOCAL_PATH - путь к файлу на вашем компьютере.
    """
    target = remote_path or f"/(auto)"
    click.echo(f"⏳ Загружаю {local_path} → {target}")
    success = upload_file(local_path, remote_path)
    if success:
        click.secho("✅ Файл успешно загружен.", fg="green")
    else:
        click.secho("❌ Ошибка при загрузке файла.", fg="red")


@cli.command()
@click.argument('remote_path')
@click.argument('local_path', required=False)
def download(remote_path, local_path):
    """Скачивание файла из облака.

    REMOTE_PATH – путь в облаке (например /docs/report.pdf).
    LOCAL_PATH – куда сохранить (по умолчанию тек. каталог и исходное имя).
    """
    dst = local_path or '(текущая папка)'
    click.echo(f"⏳ Скачиваю {remote_path} → {dst}")
    success = download_file(remote_path, local_path)
    if success:
        click.secho("✅ Файл скачан.", fg="green")
    else:
        click.secho("❌ Ошибка скачивания.", fg="red")


@cli.command()
@click.argument('local_dir', default='.')
@click.argument('remote_dir', default='/')
@click.option('--direction', '-d', type=click.Choice(['push', 'pull', 'both'], case_sensitive=False),
              default='both', show_default=True,
              help="Направление: push (локальное → облако), pull (облако → локальное), both (двусторонняя)")
def sync(local_dir, remote_dir, direction):
    """Синхронизация каталогов LOCAL_DIR и REMOTE_DIR."""
    arrow = {
        'push': '→',
        'pull': '←',
        'both': '↔',
    }[direction.lower()]
    click.echo(f"⏳ Синхронизация {local_dir} {arrow} {remote_dir} (mode: {direction})")
    sync_directories(local_dir, remote_dir, direction.lower())
    click.secho("✅ Синхронизация завершена.", fg="green")


@cli.command(name='rm')
@click.argument('remote_path')
def cmd_rm(remote_path):
    """Удалить файл/папку в облаке."""
    click.echo(f"⏳ Удаляю {remote_path} …")
    if delete_file(remote_path):
        click.secho("✅ Удалено.", fg="green")
    else:
        click.secho("❌ Ошибка удаления.", fg="red")


@cli.command(name='mv')
@click.argument('src_path')
@click.argument('dst_path')
def cmd_mv(src_path, dst_path):
    """Переименовать/переместить файл в облаке."""
    click.echo(f"⏳ Перемещаю {src_path} → {dst_path}")
    if move_file(src_path, dst_path):
        click.secho("✅ Готово.", fg="green")
    else:
        click.secho("❌ Ошибка перемещения.", fg="red")


@cli.command()
@click.argument('remote_path')
def info(remote_path):
    """Показать информацию о файле (size, modified и т.п.)."""
    data = file_info(remote_path)
    if not data:
        click.secho("❌ Не удалось получить информацию.", fg="red")
        return
    for k, v in data.items():
        click.echo(f"{k}: {v}")
