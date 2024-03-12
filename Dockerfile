# syntax=docker/dockerfile:1

FROM python:3.11-alpine

WORKDIR /app

RUN pip install --upgrade pip
RUN apk add --no-cache openssl-dev libffi-dev build-base

COPY . .
RUN pip3 install -r requirements.txt

CMD ["python3", "bot.py"]
