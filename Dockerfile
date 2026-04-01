FROM tiangolo/uwsgi-nginx-flask:python3.11

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME && \
    $POETRY_HOME/bin/pip install poetry==2.0.0 && \
    $POETRY_HOME/bin/poetry config virtualenvs.create false

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN $POETRY_HOME/bin/poetry install

RUN mkdir -p /app/ms365_accountcreator /app/instance /app-mnt

COPY docker/uwsgi.ini docker/logging_config.json /app/
COPY docker/ms365_accountcreator.conf /app/instance/
COPY docker/prestart.sh /app/prestart.sh
COPY ms365_accountcreator /app/ms365_accountcreator

ENV STATIC_PATH=/app/ms365_accountcreator/static
ENV FLASK_APP=ms365_accountcreator
ENV MODE=production
ENV CONFIG_FILE=/app-mnt/ms365_accountcreator.conf

RUN $POETRY_HOME/bin/poetry run pybabel compile -d ms365_accountcreator/translations
