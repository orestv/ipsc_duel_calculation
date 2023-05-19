FROM python:3.11-slim
WORKDIR /app

RUN pip install pipenv
COPY Pipfile* .

RUN pipenv sync
COPY duels duels

CMD pipenv run uvicorn --host 0.0.0.0 --port 80 duels.api:app
