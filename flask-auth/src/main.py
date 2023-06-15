from gevent import monkey

monkey.patch_all()

import logging.config
from datetime import timedelta
from http import HTTPStatus

from api.v1 import auth_handlers, role_handlers
from config.swagger import swagger_config, template
from core.config import common_settings, jaeger_settings, jwt_settings, role_settings
from core.logger import LOGGER_CONFIG
from db.models.user import Role, User
from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from models.common import BaseResponse
from utils.exceptions import add_base_exceptions_handlers
from utils.jaeger_config import configure_jaeger_tracer

from db import alchemy, init_db

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
app.register_blueprint(auth_handlers.auth_bp)
app.register_blueprint(role_handlers.role_bp)

app.app_context().push()


@app.before_first_request
def initial_create():
    for role_name, role_description in role_settings.get_initial_roles():
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name, description=role_description)
            alchemy.session.add(role)
            alchemy.session.commit()


if __name__ == "__main__":
    initial_create()
    app.run(
        host=common_settings.host,
        port=common_settings.port,
        debug=common_settings.debug,
    )
