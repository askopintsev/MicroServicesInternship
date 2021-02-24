import os
from email.message import EmailMessage
from dotenv import load_dotenv

import aiosmtplib
import asyncio
import aio_pika


load_dotenv()
rabbit_user = os.environ.get("RABBIT_USER")
rabbit_pass = os.environ.get("RABBIT_PASSWORD")


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


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        await send_email(message.body.decode("utf-8"))


async def main(loop):

    connection = await aio_pika.connect_robust(f"amqp://{rabbit_user}:{rabbit_pass}@rabbit:5672/", loop=loop)

    queue_name = "mails"

    # Creating channel
    channel = await connection.channel()

    # Maximum message count which will be
    # processing at the same time.
    await channel.set_qos(prefetch_count=100)

    # Declaring queue
    queue = await channel.declare_queue(queue_name, auto_delete=True)

    await queue.consume(process_message)

    return connection


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(main(loop))

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())
