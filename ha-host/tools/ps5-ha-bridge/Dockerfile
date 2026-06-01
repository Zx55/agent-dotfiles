ARG BUILD_ARCH=aarch64
FROM ghcr.io/home-assistant/${BUILD_ARCH}-base:latest

RUN apk add --no-cache python3 py3-pip

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN python3 -m venv /opt/ps5-ha-bridge \
  && /opt/ps5-ha-bridge/bin/pip install --no-cache-dir /app

COPY run.sh /run.sh
RUN chmod 755 /run.sh

CMD ["/run.sh"]
