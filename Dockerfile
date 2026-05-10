FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install poetry-core
RUN pip install -e .

CMD ["moneypype", "/app/src/moneypype/data/raw/2026-04-06_budget.csv"]