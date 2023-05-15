FROM python:3.10
WORKDIR /fastapi/tests
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT python wait_services.py && pytest ./src