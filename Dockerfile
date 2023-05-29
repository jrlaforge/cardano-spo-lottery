FROM python:3.9-slim-buster

COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

RUN mkdir -p /src
COPY src/ /src/
RUN pip install -e /src
COPY alembic/ /src/alembic/

COPY entrypoint.sh /src/
COPY gunicorn-cfg.py /src/
COPY alembic-docker.ini /src/alembic.ini
WORKDIR /src
#ENV FLASK_APP=flask_app.py FLASK_DEBUG=1 PYTHONUNBUFFERED=1
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/src/entrypoint.sh"]
