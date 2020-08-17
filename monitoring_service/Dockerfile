# Base Image
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /monitoring_service
WORKDIR /monitoring_service
COPY ./monitoring_service /monitoring_service/
RUN pip install poetry
RUN poetry install
