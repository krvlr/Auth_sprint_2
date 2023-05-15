from core.config import MIGRATION_DIR, postgre_settings
from flask import Flask, current_app
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=convention)
alchemy = SQLAlchemy(metadata=metadata)


def init_db(app: Flask):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = postgre_settings.get_db_uri()
    alchemy.init_app(app)
    Migrate(app, alchemy, MIGRATION_DIR)
