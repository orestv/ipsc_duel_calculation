FROM python:3.12-slim
WORKDIR /app

RUN pip install pipenv
COPY Pipfile* .

RUN pipenv sync && pipenv run pip install beautifulsoup4
COPY duels duels

CMD pipenv run uvicorn --host 0.0.0.0 --port 80 duels.api:app
