import click
from auth import login
from api import list_files

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
def ls():
    """Список файлов в корне облака"""
    files = list_files("/")
    for f in files:
        click.echo(f)
