# Base Image
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /mail_service
WORKDIR /mail_service
COPY /mail_service /mail_service/
RUN pip install poetry
RUN poetry install
