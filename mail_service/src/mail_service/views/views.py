import os

import aio_pika
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from mail_service.src.mail_service.models.models import MailModel, Mail, SendingMail

load_dotenv()
rabbit_user = os.environ.get("RABBIT_USER")
rabbit_pass = os.environ.get("RABBIT_PASSWORD")

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


@router.post("/mails/add")
async def add_mail(mail: MailModel):
    new_mail = await Mail.create(text=mail.text)
    return JSONResponse(new_mail.to_dict())


@router.delete("/mails/delete/{mail_id}")
async def delete_mail(mail_id: int):
    mail = await Mail.get_or_404(mail_id)
    await mail.delete()
    return JSONResponse(dict(id=mail_id))


@router.post("/send/{mail_id}")
async def send_to_queue(params: SendingMail):

    params_dict = {
        "username": params.username,
        "password": params.password,
        "short_descr": params.short_descr,
        "full_descr": params.full_descr,
        "price": params.price,
        "created_at": params.created_at,
    }

    mail_text = await Mail.select("text").where(Mail.id == params.mail_id).gino.scalar()

    sending_text = await format_mail_text(mail_text, params_dict)

    sending_result = await send_to_rabbit(sending_text)

    return JSONResponse(sending_result)


async def format_mail_text(input_text, params_dict):
    output_text = str(input_text).format(**params_dict)
    return output_text


async def send_to_rabbit(sending_text):
    connection = await aio_pika.connect_robust(f"amqp://{rabbit_user}:{rabbit_pass}@rabbit:5672/")

    async with connection:
        routing_key = "mails"

        channel = await connection.channel()

        await channel.default_exchange.publish(aio_pika.Message(body=sending_text.format(routing_key).encode()),
                                               routing_key=routing_key,
                                               )

        return {"Result": "Mail was sent to queue"}
