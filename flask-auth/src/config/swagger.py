template = {
    "swagger": "2.0",
    "info": {
        "title": "Сервис аутентификации",
        "description": "API сервис для аутентификации и авторизации пользователей.",
        "contact": {},
        "version": "1.0",
    },
    "basePath": "/api/v1",
    "schemes": [
        "http",
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Заголовок авторизации JWT с использованием схемы Bearer."
            'Пример: "Authorization: Bearer {token}"',
        }
    },
}

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/openapi.json",
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/openapi",
}
