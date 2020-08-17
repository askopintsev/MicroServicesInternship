import os
from typing import Optional

import pika
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..models.mails import Mail

load_dotenv()

router = APIRouter()


@router.get("/mails/{mail_id}")
async def get_single_mail(mail_id: int):
    mail = await Mail.get_or_404(mail_id)
    return JSONResponse(mail.to_dict())


@router.get("/mails")
async def get_all_mails():
    mails = await Mail.select("id", "text").gino.all()
    result_dict = dict(mails)
    return JSONResponse(result_dict)


class MailModel(BaseModel):
    text: str


@router.post("/mails/add")
async def add_mail(mail: MailModel):
    rv = await Mail.create(text=mail.text)
    return JSONResponse(rv.to_dict())


@router.delete("/mails/delete/{mail_id}")
async def delete_mail(mail_id: int):
    mail = await Mail.get_or_404(mail_id)
    await mail.delete()
    return JSONResponse(dict(id=mail_id))


@router.post("/send/{mail_id}")
async def send_to_queue(
    mail_id: int,
    username: Optional[str] = None,
    password: Optional[str] = None,
    short_descr: Optional[str] = None,
    full_descr: Optional[str] = None,
    price: Optional[int] = None,
    created_at: Optional[str] = None,
):

    params_dict = {
        "username": username,
        "password": password,
        "short_descr": short_descr,
        "full_descr": full_descr,
        "price": price,
        "created_at": created_at,
    }

    mail_text = await Mail.select("text").where(Mail.id == mail_id).gino.scalar()

    sending_text = await format_mail_text(mail_text, params_dict)

    sending_result = await send_to_rabbit(sending_text)

    return JSONResponse(sending_result)


async def format_mail_text(input_text, params_dict):
    output_text = str(input_text).format(**params_dict)
    return output_text


async def send_to_rabbit(sending_text):
    credentials = pika.PlainCredentials(
        os.environ.get("RABBIT_USER"), os.environ.get("RABBIT_PASSWORD")
    )

    parameters = pika.ConnectionParameters("rabbit", 5672, "/", credentials)

    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.queue_declare(queue="mails")
    channel.basic_publish(exchange="", routing_key="mails", body=sending_text)
    connection.close()

    return {"Result": "Mail was sent to queue"}


def init_app(app):
    app.include_router(router)
