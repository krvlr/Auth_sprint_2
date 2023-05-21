from http import HTTPStatus

from gevent import monkey
from jaeger_config import configure_jaeger_tracer
from models.common import BaseResponse

monkey.patch_all()

from db.models.user import User, Role
from utils.exceptions import add_base_exceptions_handlers

import logging.config
from datetime import timedelta

from api.v1 import auth_handler
from core.config import flask_settings, jwt_settings, role_settings, jaeger_settings
from core.logger import LOGGER_CONFIG
from db import init_db, alchemy
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from config.swagger import template, swagger_config

logging.config.dictConfig(LOGGER_CONFIG)


def create_app():
    app = Flask(__name__)

    configure_jaeger_tracer(app, jaeger_settings.host, jaeger_settings.port)

    Swagger(app, template=template, config=swagger_config)

    app.config["JWT_COOKIE_SECURE"] = jwt_settings.cookie_secure
    app.config["JWT_TOKEN_LOCATION"] = jwt_settings.token_location.split(", ")
    app.config["JWT_SECRET_KEY"] = jwt_settings.secret_key
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=jwt_settings.access_token_expires)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(hours=jwt_settings.refresh_token_expires)

    add_base_exceptions_handlers(app)

    @app.before_request
    def before_request():
        request_id = request.headers.get("X-Request-Id")
        if not request_id:
            return (
                jsonify(
                    BaseResponse(
                        success=False, error="Ошибка формата входных данных. Отсутствует request id"
                    ).dict()
                ),
                HTTPStatus.BAD_REQUEST,
            )

    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        return User.query.filter_by(id=jwt_data["sub"]["id"]).one_or_none()

    init_db(app)

    return app


app = create_app()
app.register_blueprint(auth_handler.auth_bp)


app.app_context().push()
# это можно было использовать вместо alembic миграций
# что в свою очередь сэкономило бы тонну времени
# alchemy.create_all()


@app.before_first_request
def initial_create():
    for role_name, role_description in role_settings.get_initial_roles():
        # функциональности по upsert в sqlalchemy не нашел
        # если честно так и не понял в чем кайф всех этих миграций
        # кучи времени на описание таблиц,
        # поисков зацикленных ипортов,
        # когда есть psycopg2 и SQL
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=role_description)
            alchemy.session.add(role)
            alchemy.session.commit()


if __name__ == "__main__":
    initial_create()
    app.run(
        host=flask_settings.host,
        port=flask_settings.port,
        debug=flask_settings.debug,
    )
