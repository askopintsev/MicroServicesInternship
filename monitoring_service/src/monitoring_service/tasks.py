import os
from datetime import datetime

import celery_pool_asyncio
from celery import Celery
from dotenv import load_dotenv
from gino import create_engine

from .config import DB_DSN
from .models.events import Event

load_dotenv()
login = str(os.environ.get("RABBIT_USER"))
password = str(os.environ.get("RABBIT_PASSWORD"))

app = Celery("tasks", broker="amqp://" + login + ":" + password + "@rabbit:5672")


@app.task(name="tasks.add_to_db")
async def add_to_db(request_timestamp, service, url, status_code, response_time):

    engine = await create_engine(DB_DSN)
    await Event.create(
        request_timestamp=datetime.fromisoformat(request_timestamp),
        service=service,
        url=url,
        status_code=status_code,
        response_time=datetime.fromisoformat(response_time),
        bind=engine,
    )
    await engine.close()
