FROM python:3.14-slim

WORKDIR /app

RUN groupadd -r cta && useradd -r -g cta -d /app -s /bin/false cta

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]" && \
    rm -rf /root/.cache/pip

COPY --chown=cta:cta . .

RUN mkdir -p /app/data/db /app/data/storage /app/data/exports /app/data/backups && \
    chown -R cta:cta /app/data

USER cta

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import http.client; http.client.HTTPConnection('localhost', 8000).request('GET', '/health'); r = http.client.HTTPConnection('localhost', 8000).getresponse(); exit(0) if r.status == 200 else exit(1)"

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
