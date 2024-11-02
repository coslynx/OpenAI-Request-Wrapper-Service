FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL=postgresql://user:password@localhost:5432/openai_wrapper \
    OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE \
    JWT_SECRET=YOUR_JWT_SECRET_HERE \
    REDIS_URL=redis://localhost:6379

EXPOSE 8000 9100

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]