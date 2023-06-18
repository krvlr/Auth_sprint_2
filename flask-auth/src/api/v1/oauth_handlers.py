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

google_oauth_bp = Blueprint("google_oauth", __name__, url_prefix="/google")
yandex_oauth_bp = Blueprint("yandex_oauth", __name__, url_prefix="/yandex")

oauth_service = get_oauth_service()


@google_oauth_bp.route("/signin", methods=["GET"])
def google_signin():
    redirect_uri = url_for("api_auth.google_oauth.google_signin_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri), HTTPStatus.OK


@google_oauth_bp.route("/callback", methods=["GET"])
@log_action
def google_signin_callback():
    try:
        token = oauth.google.authorize_access_token()
        user = GoogleUser(**token["userinfo"])

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


@yandex_oauth_bp.route("/signin", methods=["GET"])
def yandex_signin():
    url = url_for("api_auth.yandex_oauth.yandex_signin_callback", _external=True)
    return oauth.yandex.authorize_redirect(url), HTTPStatus.OK


@yandex_oauth_bp.route("/callback", methods=["GET"])
@log_action
def yandex_signin_callback():
    try:
        oauth.yandex.authorize_access_token()

        user_info = oauth.yandex.get(oauth_yandex_settings.user_info_url)
        user = YandexUser(**user_info.json())

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
