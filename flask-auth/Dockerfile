FROM python:3.10
WORKDIR /opt/app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir
COPY src .
ENTRYPOINT flask --app main db upgrade && gunicorn --worker-class gevent --workers 1 --bind 0.0.0.0:8000 main:app