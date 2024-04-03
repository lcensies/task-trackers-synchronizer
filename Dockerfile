FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

RUN apt update -qqy && apt -qqy full-upgrade && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

WORKDIR /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org/ | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
        ln -s /opt/poetry/bin/poetry && \
            poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY ./app /app/app
ENV VARIABLE_NAME=api
ENV PYTHONPATH=/api
