FROM ghcr.io/linuxserver/baseimage-alpine:3.19
LABEL org.opencontainers.image.source="https://github.com/speedyconzales/series-scraper"

WORKDIR /app

COPY . /app/

COPY root/ /

RUN chmod +x /etc/s6-overlay/s6-rc.d/init-series-scraper-config/run

RUN apk update && apk add --no-cache python3 py3-pip chromium chromium-chromedriver ffmpeg

RUN python3 -m pip install -r requirements.txt --break-system-packages

RUN python -c "from src.html_scraper import find_and_unzip_crx; find_and_unzip_crx()" && rm src/extensions/recaptcha-solver.crx
