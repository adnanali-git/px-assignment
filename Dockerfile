# --------------------------
# Stage 1: Build Dependencies
# --------------------------
FROM python:3.12-slim AS builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --------------------------
# Stage 2: Final Runtime
# --------------------------
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

# Start FastAPI in dev mode using `fastapi` CLI
CMD ["fastapi", "dev", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
