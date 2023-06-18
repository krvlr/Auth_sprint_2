from http import HTTPStatus

from flasgger import swag_from
from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import current_user, get_jti, get_jwt, jwt_required
from models.auth_models import (
    AuthResponse,
    PaginatorRequest,
    PasswordChangeRequest,
    SigninRequest,
    SignoutRequest,
    SignupRequest,
)
from models.common import BaseResponse
from services.auth_service import get_auth_service
from utils.common import get_data_from_body, get_data_from_params, set_jwt_in_cookie
from utils.exceptions import (
    AccountHistoryException,
    AccountPasswordChangeException,
    AccountRefreshException,
    AccountSigninException,
    AccountSignoutAllException,
    AccountSignoutException,
    AccountSignupException,
)
from utils.rate_limit import limit_leaky_bucket
from utils.user_action import log_action

auth_bp = Blueprint("auth", __name__)
auth_service = get_auth_service()


@auth_bp.route("/signup", methods=["POST"])
@log_action
@swag_from("docs/auth/signup.yaml")
def signup():
    try:
        body = get_data_from_body(SignupRequest)
        user_data = auth_service.signup(
            login=body.login,
            email=body.email,
            password=body.password,
        )
        return jsonify(BaseResponse(data=user_data).dict()), HTTPStatus.CREATED
    except AccountSignupException as ex:
        return (
            jsonify(BaseResponse(success=False, error=ex.error_message).dict()),
            HTTPStatus.BAD_REQUEST,
        )


@auth_bp.route("/signin", methods=["POST"])
@log_action
@swag_from("docs/auth/signin.yaml")
def signin():
    try:
        body = get_data_from_body(SigninRequest)
        auth_data = AuthResponse(
            **auth_service.signin(
                login=body.login,
                password=body.password,
            )
        )

        response = jsonify(BaseResponse(data=dict(auth_data)).dict())

        set_jwt_in_cookie(
            response=response,
            access_token=auth_data.access_token,
            refresh_token=auth_data.refresh_token,
        )

        return response, HTTPStatus.OK
    except AccountSigninException as ex:
        return (
            jsonify(BaseResponse(success=False, error=ex.error_message).dict()),
            HTTPStatus.UNAUTHORIZED,
        )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
@limit_leaky_bucket
@log_action
@swag_from("docs/auth/refresh.yaml")
def refresh():
    try:
        refresh_jwt_info = get_jwt()
        auth_data = AuthResponse(
            **auth_service.refresh(
                user=current_user,
                device_info=refresh_jwt_info["sub"]["device_info"],
                refresh_jti=refresh_jwt_info["jti"],
            )
        )

        response = jsonify(BaseResponse(data=dict(auth_data)).dict())

        set_jwt_in_cookie(
            response=response,
            access_token=auth_data.access_token,
            refresh_token=auth_data.refresh_token,
        )

        return response, HTTPStatus.OK
    except AccountRefreshException as ex:
        return (
            jsonify(BaseResponse(success=False, error=ex.error_message).dict()),
            HTTPStatus.BAD_REQUEST,
        )


@auth_bp.route("/password/change", methods=["POST"])
@jwt_required()
@limit_leaky_bucket
@log_action
@swag_from("docs/auth/password_change.yaml")
def password_change():
    try:
        body = get_data_from_body(PasswordChangeRequest)

        auth_service.password_change(
            user=current_user,
            access_jti=get_jwt()["jti"],
            old_password=body.old_password,
            new_password=body.new_password,
        )
        return (
            jsonify(BaseResponse(success=True).dict()),
            HTTPStatus.OK,
        )
    except AccountPasswordChangeException as ex:
        return (
            jsonify(BaseResponse(success=False, error=ex.error_message).dict()),
            HTTPStatus.BAD_REQUEST,
        )


@auth_bp.route("/signout", methods=["POST"])
@jwt_required()
@limit_leaky_bucket
@log_action
@swag_from("docs/auth/signout.yaml")
def signout():
    try:
        body = get_data_from_body(SignoutRequest)

        auth_service.signout(
            user_id=current_user.id,
            refresh_jti=get_jti(body.refresh_token),
            access_jti=get_jwt()["jti"],
        )

        return jsonify(BaseResponse().dict()), HTTPStatus.OK
    except AccountSignoutException as error:
        return (
            jsonify(BaseResponse(success=False, error=error.error_message).dict()),
            HTTPStatus.BAD_REQUEST,
        )


@auth_bp.route("/signout/all", methods=["POST"])
@jwt_required()
@limit_leaky_bucket
@log_action
@swag_from("docs/auth/signout_all.yaml")
def signout_all():
    try:
        auth_service.signout_all(user_id=current_user.id, access_jti=get_jwt()["jti"])

        return jsonify(BaseResponse().dict()), HTTPStatus.OK
    except AccountSignoutAllException as error:
        return (
            jsonify(BaseResponse(success=False, error=error.error_message).dict()),
            HTTPStatus.BAD_REQUEST,
        )


@auth_bp.route("/history", methods=["GET"])
@jwt_required()
@limit_leaky_bucket
@swag_from("docs/auth/history.yaml")
def history():
    try:
        paginator = get_data_from_params(PaginatorRequest)
        history = auth_service.history(
            user_id=current_user.id,
            access_jti=get_jwt()["jti"],
            page_size=paginator.page_size,
            page_num=paginator.page_num,
        )

        return jsonify(BaseResponse(data=history).dict()), HTTPStatus.OK
    except AccountHistoryException as error:
        return (
            jsonify(BaseResponse(success=False, error=error.error_message).dict()),
            HTTPStatus.BAD_REQUEST,
        )


@auth_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify(BaseResponse().dict()), HTTPStatus.OK
