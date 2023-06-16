from flask import Blueprint

from api.v1.auth_handlers import auth_bp
from api.v1.oauth_handlers import google_oauth_bp, yandex_oauth_bp

api_auth_bp = Blueprint("api_auth", __name__, url_prefix="/api/v1")
api_auth_bp.register_blueprint(auth_bp)
api_auth_bp.register_blueprint(google_oauth_bp)
api_auth_bp.register_blueprint(yandex_oauth_bp)
