import os
from datetime import datetime

from celery import Celery
from dotenv import load_dotenv
from gino import create_engine

from monitoring_service.src.monitoring_service.config import DB_DSN
from monitoring_service.src.monitoring_service.models.models import Event

load_dotenv()
login = str(os.environ.get("RABBITMQ_USER"))
password = str(os.environ.get("RABBITMQ_PASS"))

broker = "amqp://guest:guest@rabbit:5672"

app = Celery("tasks", broker=broker)


@app.task(name="tasks.add_to_db")
async def add_to_db(request_timestamp, service, url, status_code, response_time):

    engine = await create_engine(DB_DSN)
    await Event.create(
        request_timestamp=datetime.strptime(request_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ'),
        service=service,
        url=url,
        status_code=status_code,
        response_time=datetime.strptime(response_time, '%Y-%m-%dT%H:%M:%S.%fZ'),
        bind=engine,
    )
    await engine.close()

    return {"status": True}
