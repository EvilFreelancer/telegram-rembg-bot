FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN set -xe  \
 && apt update \
 && apt install -fyq pkgconf mariadb-client libmariadb-dev build-essential \
 && pip install -U pip wheel setuptools \
 && pip install -r requirements.txt \
 && pip cache purge \
 && apt purge -y --auto-remove build-essential \
 && apt clean \
 && rm -rf /var/lib/apt/lists/*
COPY . .
EXPOSE 5000
ENTRYPOINT ["python", "/app/bot.py"]
