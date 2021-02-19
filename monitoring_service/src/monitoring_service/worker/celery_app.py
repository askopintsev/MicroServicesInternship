import os

from celery import Celery
from dotenv import load_dotenv

from monitoring_service.src.monitoring_service.config import DB_DSN

load_dotenv()
login = str(os.environ.get("RABBITMQ_USER"))
password = str(os.environ.get("RABBITMQ_PASS"))

celery_app = Celery("event_writer",
                    backend='db+' + DB_DSN,
                    broker="amqp://guest:guest@rabbit:5672"
                    )

celery_app.conf.task_routes = {"monitoring_service.src.monitoring_service.worker.celery_worker.add_to_db_task": "celery"}
celery_app.conf.update(task_track_started=True)
