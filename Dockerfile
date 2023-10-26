FROM python:3

RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates \
        apt-utils \
        gnupg \
        dirmngr \
        build-essential \
        git \
        curl \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*

RUN curl https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb --output google-chrome-stable_current_amd64.deb \
    && apt-get update && apt-get install ./google-chrome-stable_current_amd64.deb -y && rm ./google-chrome-stable_current_amd64.deb

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./rapidaproject /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]

EXPOSE 3000
EXPOSE 1433
EXPOSE 8889
EXPOSE 5432

