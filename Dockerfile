# Multi-stage lightweight production container for CIHIP National Portal
FROM python:3.12-alpine

WORKDIR /app

# Create non-root user for Zero-Trust container security
RUN addgroup -S cihip && adduser -S cihip -G cihip

# Copy application files
COPY app/ ./app/
COPY server.py ./
COPY requirements.txt ./

# Fix ownership
RUN chown -R cihip:cihip /app

USER cihip

ENV PYTHONUNBUFFERED=1 \
    PORT=8080 \
    CIHIP_HOST=0.0.0.0

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/').read()" || exit 1

CMD ["python", "server.py"]
