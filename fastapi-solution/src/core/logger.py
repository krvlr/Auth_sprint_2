from core.config import settings


def get_logging_config_dict(log_level):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": settings.log_format},
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
            },
        },
        "handlers": {
            "console": {
                "level": log_level,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "handlers": settings.log_default_handlers,
                "level": log_level,
            },
            "uvicorn.error": {
                "level": log_level,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": log_level,
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "formatter": "verbose",
            "handlers": settings.log_default_handlers,
        },
    }
