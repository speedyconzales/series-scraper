# Stage 1: Checkout repository and prepare environment
FROM ghcr.io/linuxserver/baseimage-alpine:edge AS builder

# Set the working directory
WORKDIR /app

# Install git and git-lfs for cloning the repository
RUN apk update && apk add git git-lfs
RUN git lfs install

# Copy the current directory contents into the container at /
RUN git clone https://github.com/speedyconzales/series-scraper.git /app

RUN mv template.yml config.yml

# Stage 2: Final setup
FROM ghcr.io/linuxserver/baseimage-alpine:edge
LABEL org.opencontainers.image.source="https://github.com/speedyconzales/seroes-scraper"

WORKDIR /app

RUN apk update

# Install Python 3
RUN apk add --no-cache python3=~3.12 py3-pip

COPY --from=builder /app /app

# Install any needed packages specified in requirements.txt
RUN python3 -m pip install -r requirements.txt --break-system-packages

# Install Chromium
RUN apk add --no-cache chromium

# Install Chromium driver
RUN apk add --no-cache chromium-chromedriver

# Install FFmpeg
RUN apk add --no-cache ffmpeg

#ENTRYPOINT ["/bin/sh", "-c", "exec /init; python3 /app/main.py"]
