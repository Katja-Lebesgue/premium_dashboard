FROM python:3.10

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python - --version 1.4.2 && cd /usr/local/bin && ln -s /opt/poetry/bin/poetry && poetry config virtualenvs.create true && poetry config virtualenvs.in-project true

# Copy poetry.lock* in case it doesn't exist in the repo
COPY pyproject.toml poetry.lock* /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "poetry install --no-root"

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY . /app

RUN python3.10 -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon');"

CMD ["sleep", "infinity"]
