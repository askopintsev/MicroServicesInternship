from fastapi import FastAPI

from mail_service.src.mail_service.database import db
from mail_service.src.mail_service.views.views import router


def get_app():
    app = FastAPI(title="Mail service")
    app.include_router(router)
    db.init_app(app)

    return app


app = get_app()
