from . import db


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.BigInteger(), primary_key=True)
    request_timestamp = db.Column(db.DateTime(), nullable=False)
    service = db.Column(db.String(), nullable=False)
    url = db.Column(db.String(), nullable=False)
    status_code = db.Column(db.Integer(), nullable=False)
    response_time = db.Column(db.DateTime(), nullable=False)
