FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=120
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefer-binary -e .

COPY app/ app/
COPY templates/ templates/
COPY tests/ tests/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
