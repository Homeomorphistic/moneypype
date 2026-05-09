FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install poetry-core
RUN pip install -e .

CMD ["moneypype"]