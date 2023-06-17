from gevent import monkey

monkey.patch_all()

import logging.config
from datetime import timedelta
from http import HTTPStatus

from api.v1 import auth_handlers
from models.common import BaseResponse

from flasgger import Swagger
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager

from api.v1 import api_auth_bp
from api.v1.oauth_handlers import oauth
from config.swagger import template, swagger_config
from core.config import (
    common_settings,
    jwt_settings,
    role_settings,
    oauth_google_settings,
    oauth_yandex_settings,
)
from core.config import jaeger_settings
from core.logger import LOGGER_CONFIG
from db import init_db, alchemy
from db.models.user import User, Role
from utils.click_commands import create_admin
from utils.exceptions import add_base_exceptions_handlers
from utils.jaeger_config import configure_jaeger_tracer

logging.config.dictConfig(LOGGER_CONFIG)


def create_app():
    app = Flask(__name__)

    configure_jaeger_tracer(app, jaeger_settings.host, jaeger_settings.port)

    Swagger(app, template=template, config=swagger_config)

    app.config["SECRET_KEY"] = common_settings.secret_key

    app.config.update(
        {
            "JWT_COOKIE_SECURE": jwt_settings.cookie_secure,
            "JWT_TOKEN_LOCATION": jwt_settings.token_location.split(", "),
            "JWT_SECRET_KEY": jwt_settings.secret_key,
            "JWT_ACCESS_TOKEN_EXPIRES": timedelta(hours=jwt_settings.access_token_expires),
            "JWT_REFRESH_TOKEN_EXPIRES": timedelta(hours=jwt_settings.refresh_token_expires),
        }
    )

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

    oauth.init_app(app)
    app.config.update(
        {
            "GOOGLE_CLIENT_ID": oauth_google_settings.client_id,
            "GOOGLE_CLIENT_SECRET": oauth_google_settings.client_secret,
        }
    )
    oauth.register(
        "google",
        server_metadata_url=oauth_google_settings.conf_url,
        client_kwargs={"scope": oauth_google_settings.scope},
    )

    app.config.update(
        {
            "YANDEX_CLIENT_ID": oauth_yandex_settings.client_id,
            "YANDEX_CLIENT_SECRET": oauth_yandex_settings.client_secret,
            "YANDEX_ACCESS_TOKEN_URL": oauth_yandex_settings.access_token_url,
            "YANDEX_AUTHORIZE_URL": oauth_yandex_settings.authorize_url,
        }
    )
    oauth.register("yandex")

    app.cli.add_command(create_admin)

    return app


app = create_app()
app.register_blueprint(auth_handlers.auth_bp)
app.register_blueprint(api_auth_bp)

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
