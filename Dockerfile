# app/Dockerfile

FROM python:3.7.15-slim-buster

WORKDIR /app

ENV RUN_TIME5=1235

RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

copy . .

RUN pip3 install -r requirements.txt

ENTRYPOINT ["streamlit", "run", "app.py"]