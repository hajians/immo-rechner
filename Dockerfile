FROM python:3.11-buster

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /immo-rechner

COPY poetry.lock pyproject.toml ./
COPY immo_rechner ./immo_rechner

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR

ENTRYPOINT ["poetry", "run", "gunicorn", "-b", "0.0.0.0:8008", "-w", "4", "immo_rechner.app.app:get_server()"]
