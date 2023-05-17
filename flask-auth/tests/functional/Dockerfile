FROM python:3.10
WORKDIR /flask/tests
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
ENTRYPOINT python wait_services.py && pytest ./src