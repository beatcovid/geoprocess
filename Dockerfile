# FROM python:3.8-alpine3.11 as poetry
FROM python:3.8 as poetry

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.5

RUN pip install "poetry==$POETRY_VERSION"

RUN apt -y update && apt-get -y install binutils libproj-dev gdal-bin

FROM poetry as base
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.in-project true && \
  poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
FROM base

COPY . /code
WORKDIR /code

RUN mkdir -p /var/cache

ENTRYPOINT [ "./docker-entrypoint.sh" ]
CMD huey_consumer geoprocess.scheduler.huey
