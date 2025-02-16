FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8080 8000

CMD ["sh", "-c", "airflow db init && airflow webserver -p 8080 & airflow scheduler & uvicorn app:app --reload"]
