from fastapi import APIRouter
from fastapi.responses import JSONResponse

from monitoring_service.src.monitoring_service.models.models import EventModel, Event

from monitoring_service.src.monitoring_service.worker.celery_app import celery_app

router = APIRouter()


@router.post("/events/add")
async def add_event(event: EventModel):
    event_data = {'request_timestamp': event.request_timestamp.replace(tzinfo=None),
                  'service': event.service,
                  'url': event.url,
                  'status_code': event.status_code,
                  'response_time': event.response_time.replace(tzinfo=None)
                  }

    # event = await Event.create(**event_data)
    task = celery_app.send_task("monitoring_service.src.monitoring_service.worker.celery_worker.add_to_db_task",
                                kwargs=event_data)

    return JSONResponse(content="Event recorded successfully", status_code=200)


@router.get("/events/all")
async def get_all_events():
    all_events = await Event.query.gino.all()
    return all_events
