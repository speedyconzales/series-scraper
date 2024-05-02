FROM ghcr.io/linuxserver/baseimage-debian:bookworm
LABEL org.opencontainers.image.source="https://github.com/speedyconzales/series-scraper"

WORKDIR /app

COPY . /app/

COPY root/ /

RUN chmod +x /etc/s6-overlay/s6-rc.d/init-series-scraper-config/run

RUN apt-get update && apt-get install -y chromium chromium-driver ffmpeg python3.11-full python3-pip

RUN python3 -m pip install -r requirements.txt --break-system-packages
