FROM python:3.11-buster

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /immo-rechner

COPY poetry.lock pyproject.toml ./
COPY immo_rechner ./immo_rechner

RUN poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR

ENTRYPOINT ["poetry", "run", "app", "--debug-mode", "--host", "0.0.0.0"]