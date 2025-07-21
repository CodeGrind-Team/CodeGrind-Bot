FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    python -m playwright install-deps && \
    python -m playwright install

# Copy the source code after installing dependencies such that changes in
# the source code do not invalidate the Docker cache for dependencies.
COPY src/ /app/src/

CMD ["python", "-m", "src.main"]