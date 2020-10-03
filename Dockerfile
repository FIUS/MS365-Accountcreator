FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN pip install pipenv

COPY Pipfile /app/
RUN pipenv lock
RUN pipenv install --system

WORKDIR /app

RUN mkdir --parents /app/ms365_accountcreator
RUN mkdir --parents /app/instance
RUN mkdir /app-mnt

COPY docker/uwsgi.ini /app/
COPY docker/ms365_accountcreator.conf /app/instance
COPY logging_config.json /app/
COPY ms365_accountcreator /app/ms365_accountcreator

ENV STATIC_PATH /app/ms365_accountcreator/static
ENV FLASK_APP ms365_accountcreator
ENV MODE production
ENV CONFIG_FILE /app-mnt/ms365_accountcreator.conf

RUN pipenv run babel-compile
