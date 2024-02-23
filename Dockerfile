FROM python:3-slim
RUN mkdir -p /app /src
WORKDIR /app
# RUN apk add sqlite
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
# RUN apt-get update && apt-get install sqlite3
RUN pip install hypercorn quart tortoise-orm

# COPY officepong.sql ./init.sql
# COPY setup.py ./setup.py
COPY officepong /src/officepong
COPY pyproject.toml /src/pyproject.toml
RUN pip install /src/

ENV QUART_APP=officepong
ENV QUART_TORTOISE_DB_URL=sqlite:///app/officepong.db
RUN quart generate-schemas

# RUN echo "" | sqlite3 -batch -init /app/init.sql /app/instance/officepong.db
# CMD 
CMD hypercorn  --debug --bind 0.0.0.0:5000 --workers 2 'officepong:create_app()'
