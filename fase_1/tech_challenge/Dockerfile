# Use a slim Python image for a smaller footprint
FROM python:3.12-slim

# Install uv directly into the container
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory inside the container
WORKDIR /app

# Copy only the files needed for installation first (for better caching)
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the project itself
# --frozen ensures we use the exact versions from uv.lock
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .

# Final sync to install the project (src)
RUN uv sync --frozen --no-dev

# Expose the port FastAPI will run on
EXPOSE 8000

# Use uv run to ensure we use the virtual environment created during sync
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
