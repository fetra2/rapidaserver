FROM python:3

RUN pip install --upgrade pip
RUN apk update
RUN apk add gcc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./rapidaproject /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]
