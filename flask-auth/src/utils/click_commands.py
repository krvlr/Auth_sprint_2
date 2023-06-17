import click
from db.models.user import User
from flask.cli import with_appcontext

from db import alchemy


@click.command("create_admin")
@click.argument("login")
@click.argument("email")
@click.argument("password")
@with_appcontext
def create_admin(login: str, email: str, password: str):
    if User.query.filter_by(login=login).first():
        click.echo("Пользователь с таким логином уже существует.")
        return
    if User.query.filter_by(email=email).first():
        click.echo("Пользователь с такой почтой уже существует.")
        return

    user = User(login=login, email=email, password=password, is_admin=True)

    alchemy.session.add(user)
    alchemy.session.commit()
    click.echo("Администратор успешно создан.")
