import os
from email.message import EmailMessage
from dotenv import load_dotenv

import aiosmtplib
import asyncio
import pika


load_dotenv()


async def send_email(content):
    message = EmailMessage()
    message["From"] = os.environ.get("SENDER_MAIL")
    message["To"] = os.environ.get("SENDER_MAIL")
    message["Subject"] = "Hello from AviDjango!"
    message.set_content(str(content))

    await aiosmtplib.send(message,
                          hostname=os.environ.get("SMTP_SERVER"),
                          port=465,
                          username=os.environ.get("SENDER_MAIL"),
                          password=os.environ.get("SENDER_PASS"),
                          use_tls=True
                          )


def callback(ch, method, properties, body):
    asyncio.run(send_email(body.decode("utf-8")))


while True:
    credentials = pika.PlainCredentials(os.environ.get("RABBIT_USER"),
                                        os.environ.get("RABBIT_PASSWORD")
                                        )

    parameters = pika.ConnectionParameters('rabbit',
                                           5672,
                                           '/',
                                           credentials)
    try:
        connection = pika.BlockingConnection(parameters)

        channel = connection.channel()
        channel.queue_declare(queue='mails')
        channel.basic_consume('mails', callback, auto_ack=True)
        channel.start_consuming()
    # Don't recover if connection was closed by broker
    except pika.exceptions.ConnectionClosedByBroker:
        break
    # Don't recover on channel errors
    except pika.exceptions.AMQPChannelError:
        break
    # Recover on all other connection errors
    except pika.exceptions.AMQPConnectionError:
        continue
