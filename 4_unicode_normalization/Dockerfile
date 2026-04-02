FROM python:3.11-slim

LABEL maintainer="CTF Challenge: Scrambled"
LABEL description="Polylot Notes - Unicode Normalization CTF Challenge"

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application source
COPY app/     ./app/
COPY scripts/ ./scripts/
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8004

ENTRYPOINT ["/app/entrypoint.sh"]
