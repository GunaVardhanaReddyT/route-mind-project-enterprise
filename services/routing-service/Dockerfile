FROM python:3.10-slim

WORKDIR /app

# OR-Tools needs some libs
RUN apt-get update && apt-get install -y gcc libpq-dev libprotobuf-dev protobuf-compiler && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]