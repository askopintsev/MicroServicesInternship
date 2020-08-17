# Base Image
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /celery
WORKDIR /celery
COPY /celery_worker/requirements.txt /celery/
COPY ./monitoring_service /celery/
RUN pip install -r requirements.txt