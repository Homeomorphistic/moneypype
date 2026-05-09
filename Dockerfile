FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

COPY . .

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

CMD ["python", "-m", "moneypype.etl"]