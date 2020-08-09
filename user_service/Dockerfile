# Base Image
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /user_service
WORKDIR /user_service
COPY /user_service/requirements.txt /user_service/
RUN pip install -r requirements.txt
COPY . /user_service/
