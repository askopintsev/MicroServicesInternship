# Base Image
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /mail_sender
WORKDIR /mail_sender
COPY /mail_sender/requirements.txt /mail_sender/
RUN pip install -r requirements.txt
COPY ./mail_sender/ /mail_sender/
