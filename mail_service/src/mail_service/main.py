import logging
from importlib.metadata import entry_points

from fastapi import FastAPI

from .models import db


def get_app():
    app = FastAPI(title="Mail service")
    db.init_app(app)
    load_modules(app)
    return app


logger = logging.getLogger(__name__)


def load_modules(app=None):
    for ep in entry_points()["mail_service.modules"]:
        logger.info("Loading module: %s", ep.name)
        mod = ep.load()
        if app:
            init_app = getattr(mod, "init_app", None)
            if init_app:
                init_app(app)
