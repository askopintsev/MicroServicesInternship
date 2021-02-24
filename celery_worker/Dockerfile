# Base Image
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /celery
WORKDIR /celery
COPY /monitoring_service /celery/
COPY /celery_worker/requirements.txt /celery/
RUN pip install -r requirements.txt