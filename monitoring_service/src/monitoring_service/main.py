from fastapi import FastAPI

from monitoring_service.src.monitoring_service.database import db
from monitoring_service.src.monitoring_service.views.views import router


def get_app():
    app = FastAPI(title="AviDjango monitoring service")
    app.include_router(router)
    db.init_app(app)

    return app


app = get_app()
