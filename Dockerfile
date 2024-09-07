FROM python:3.12.2-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /events

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .


RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

USER my_user
