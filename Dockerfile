FROM tiangolo/uwsgi-nginx-flask:python3.9

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_HOME=/opt/poetry
RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==2.0.0
RUN $POETRY_HOME/bin/poetry --version

WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN $POETRY_HOME/bin/poetry config virtualenvs.create false
RUN $POETRY_HOME/bin/poetry install

RUN mkdir --parents /app/ms365_accountcreator
RUN mkdir --parents /app/instance
RUN mkdir /app-mnt

COPY docker/uwsgi.ini /app/
COPY docker/ms365_accountcreator.conf /app/instance
COPY docker/logging_config.json /app/
COPY ms365_accountcreator /app/ms365_accountcreator

ENV STATIC_PATH=/app/ms365_accountcreator/static
ENV FLASK_APP=ms365_accountcreator
ENV MODE=production
ENV CONFIG_FILE=/app-mnt/ms365_accountcreator.conf

RUN $POETRY_HOME/bin/poetry run pybabel compile -d ms365_accountcreator/translations
