from datetime import datetime
from pydantic import BaseModel

from monitoring_service.src.monitoring_service.database import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.BigInteger(), primary_key=True)
    request_timestamp = db.Column(db.DateTime(), nullable=False)
    service = db.Column(db.String(), nullable=False)
    url = db.Column(db.String(), nullable=False)
    status_code = db.Column(db.Integer(), nullable=False)
    response_time = db.Column(db.DateTime(), nullable=False)


class EventModel(BaseModel):
    request_timestamp: datetime
    service: str
    url: str
    status_code: int
    response_time: datetime
