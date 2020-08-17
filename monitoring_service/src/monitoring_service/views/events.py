from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from monitoring_service.tasks import add_to_db

router = APIRouter()


class EventModel(BaseModel):
    request_timestamp: datetime
    service: str
    url: str
    status_code: int
    response_time: datetime


@router.post("/events")
async def add_event(event: EventModel):
    await add_to_db.delay(
        request_timestamp=event.request_timestamp,
        service=event.service,
        url=event.url,
        status_code=event.status_code,
        response_time=event.response_time,
    )

    return JSONResponse(content="Event recorded successfully")


def init_app(app):
    app.include_router(router)
