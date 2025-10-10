FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml README.md /app/
COPY src /app/src

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir . && \
    useradd -ms /bin/bash app && \
    chown -R app:app /app

USER app
ENV PATH="/home/app/.local/bin:${PATH}"

ENTRYPOINT ["morphoctl"]
CMD ["--help"]

