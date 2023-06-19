from http import HTTPStatus

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, url_for, jsonify

from core.config import oauth_yandex_settings
from models.auth_models import AuthResponse
from models.common import BaseResponse
from models.oauth_models import GoogleUser, YandexUser
from services.oauth_service import get_oauth_service
from utils.common import set_jwt_in_cookie
from utils.exceptions import AccountSigninException
from utils.user_action import log_action

oauth = OAuth()
oauth_service = get_oauth_service()

oauth_bp = Blueprint("social_oauth", __name__, url_prefix="/social")


@oauth_bp.route("/signin/<type>", methods=["GET"])
def signin(type):
    redirect_uri = url_for("api_auth.social_oauth.signin_callback", _external=True, type=type)

    match type:
        case "google":
            return oauth.google.authorize_redirect(redirect_uri), HTTPStatus.OK
        case "yandex":
            return oauth.yandex.authorize_redirect(redirect_uri), HTTPStatus.OK
        case other_type:
            return (
                jsonify(
                    BaseResponse(
                        success=False, error=f"Сервис {other_type} не поддерживается"
                    ).dict()
                ),
                HTTPStatus.UNAUTHORIZED,
            )


@oauth_bp.route("/callback/<type>", methods=["GET"])
@log_action
def signin_callback(type):
    try:
        match type:
            case "google":
                token = oauth.google.authorize_access_token()
                user = GoogleUser(**token["userinfo"])
            case "yandex":
                oauth.yandex.authorize_access_token()
                user_info = oauth.yandex.get(oauth_yandex_settings.user_info_url)
                user = YandexUser(**user_info.json())
            case other_type:
                raise AccountSigninException(error_message=f"Сервис {other_type} не поддерживается")

        oauth_data = AuthResponse(**oauth_service.signin_social_user(user))
        response = jsonify(BaseResponse(data=dict(oauth_data)).dict())

        set_jwt_in_cookie(
            response=response,
            access_token=oauth_data.access_token,
            refresh_token=oauth_data.refresh_token,
        )
        return response, HTTPStatus.OK

    except AccountSigninException as ex:
        return (
            jsonify(BaseResponse(success=False, error=ex.error_message).dict()),
            HTTPStatus.UNAUTHORIZED,
        )
