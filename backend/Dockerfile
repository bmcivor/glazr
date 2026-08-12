FROM python:3.14-slim-bookworm AS base

COPY --from=docker.io/astral/uv:0.11.8 /uv /usr/local/bin/uv
ENV PYTHONUNBUFFERED=1
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY pyproject.toml uv.lock ./

FROM base AS production

RUN uv sync --frozen --no-dev --no-install-project

COPY . .
USER 1000:1000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
