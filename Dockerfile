FROM python:3.9

LABEL org.opencontainers.image.source https://github.com/nuuday/paid-media-userlist/
ENV POETRY_VERSION=1.1.4
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y \
    tdsodbc \
    unixodbc-dev \
    unixodbc-bin

RUN pip install "poetry==$POETRY_VERSION" && poetry --version

WORKDIR /app
COPY ./poetry.lock ./pyproject.toml /app/

# Make sure container doesn't run as root
RUN groupadd -r web && useradd -d /app -r -g web web \
  && chown web:web -R /app
USER web

COPY --chown=web:web src/ /app/
RUN poetry install --no-interaction --no-dev

ENTRYPOINT ["/usr/local/bin/poetry", "run", "main.py"]