FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN apt-get update && \
    apt-get install -y ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

WORKDIR /app

COPY pyproject.toml /app/
COPY poetry.lock /app/
RUN /root/.poetry/bin/poetry config virtualenvs.create false
RUN /root/.poetry/bin/poetry install

RUN mkdir --parents /app/ms365_accountcreator
RUN mkdir --parents /app/instance
RUN mkdir /app-mnt

COPY docker/uwsgi.ini /app/
COPY docker/ms365_accountcreator.conf /app/instance
COPY docker/logging_config.json /app/
COPY ms365_accountcreator /app/ms365_accountcreator

ENV STATIC_PATH /app/ms365_accountcreator/static
ENV FLASK_APP ms365_accountcreator
ENV MODE production
ENV CONFIG_FILE /app-mnt/ms365_accountcreator.conf

RUN /root/.poetry/bin/poetry run pybabel compile -d ms365_accountcreator/translations
