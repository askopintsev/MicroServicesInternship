import asyncio
from datetime import datetime

from .celery_app import celery_app

from monitoring_service.src.monitoring_service.models.models import Event
from monitoring_service.src.monitoring_service.database import db
from monitoring_service.src.monitoring_service.config import DB_DSN


async def add_to_db(request_timestamp, service, url, status_code, response_time):

    async with db.with_bind(DB_DSN) as engine:
        event = await Event.create(
            request_timestamp=datetime.strptime(request_timestamp, '%Y-%m-%dT%H:%M:%S.%f'),
            service=service,
            url=url,
            status_code=status_code,
            response_time=datetime.strptime(response_time, '%Y-%m-%dT%H:%M:%S.%f'),
        )


@celery_app.task(acks_late=True)
def add_to_db_task(request_timestamp, service, url, status_code, response_time):
    asyncio.run(add_to_db(request_timestamp, service, url, status_code, response_time))
    return {"status": True}

# @celery_app.task(acks_late=True)
# async def add_to_db(request_timestamp, service, url, status_code, response_time):
#     # event = await Event.create(**event_data)
#     event = Event(
#         request_timestamp=datetime.strptime(request_timestamp, '%Y-%m-%dT%H:%M:%S.%f'),
#         service=service,
#         url=url,
#         status_code=status_code,
#         response_time=datetime.strptime(response_time, '%Y-%m-%dT%H:%M:%S.%f'),
#     )
#
#     print(event)
#     await event.create()
#
#     return {"status": True}
