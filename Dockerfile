# syntax=docker/dockerfile:1
FROM python:3.12-slim AS build
WORKDIR /src
COPY pyproject.toml LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir --prefix=/install ".[api]"

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 DETECTOR_HOST=0.0.0.0
COPY --from=build /install /usr/local
RUN useradd --system --no-create-home app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8000/api/v1/health')"
CMD ["detector-ia-server"]
