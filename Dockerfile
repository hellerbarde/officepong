FROM python:3-slim
RUN mkdir -p /app /src
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
RUN pip install hypercorn quart tortoise-orm

COPY officepong /src/officepong
COPY pyproject.toml /src/pyproject.toml
RUN pip install /src/

ENV QUART_APP=officepong
ENV QUART_TORTOISE_DB_URL=sqlite:///app/officepong.db
RUN quart generate-schemas

CMD hypercorn --bind 0.0.0.0:5000 --workers 2 'officepong:create_app()'
