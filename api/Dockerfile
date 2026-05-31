# Stage 1: Build dependency wheels
FROM python:3.10-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY shared /shared
COPY api /api

# Build wheels for shared and api packages
RUN pip install --no-cache-dir --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels /shared
RUN pip wheel --no-cache-dir --wheel-dir=/build/wheels /api

# Stage 2: Runtime image
FROM python:3.10-slim

WORKDIR /app

# Copy wheels from builder stage
COPY --from=builder /build/wheels /app/wheels

# Install wheels
RUN pip install --no-cache-dir /app/wheels/*.whl && rm -rf /app/wheels

EXPOSE 8000

ENV APP_ENV=production
ENV PORT=8000

CMD ["uvicorn", "rocket_tail_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
