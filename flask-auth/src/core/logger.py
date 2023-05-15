from core.config import logger_settings

LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {"format": logger_settings.format},
    },
    "handlers": {
        "console": {
            "level": logger_settings.level,
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
    },
    "loggers": {
        "": {
            "handlers": logger_settings.default_handlers,
            "level": logger_settings.level,
            "propagate": True,
        },
    },
}
