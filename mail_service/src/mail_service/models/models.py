from pydantic import BaseModel
from typing import Optional

from mail_service.src.mail_service.database import db


class Mail(db.Model):
    __tablename__ = "mails"

    id = db.Column(db.Integer(), primary_key=True)
    text = db.Column(db.String(), nullable=False)


class MailModel(BaseModel):
    text: str


class SendingMail(BaseModel):
    mail_id: int
    username: Optional[str] = None
    password: Optional[str] = None
    short_descr: Optional[str] = None
    full_descr: Optional[str] = None
    price: Optional[int] = None
    created_at: Optional[str] = None
