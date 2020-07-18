# Base Image
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /goods
WORKDIR /goods
COPY requirements.txt /goods
ADD . /goods
RUN pip install -r requirements.txt