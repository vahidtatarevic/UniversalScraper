FROM python:3.13-slim

# Install uv from its official image
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/

WORKDIR /app

# Compile bytecode for faster startup and copy files instead of linking
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

# Install dependencies first so this layer is cached between code changes
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Copy the application code and install the project itself
COPY . .
RUN uv sync --locked --no-dev

# Use the virtual environment by default
ENV PATH="/app/.venv/bin:$PATH"

# Use as an unprivileged user, not root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

# Trust forwarded headers from the reverse proxy so rate limits see real client IPs
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
