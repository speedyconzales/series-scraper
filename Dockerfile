# Stage 1: Checkout repository and prepare environment
FROM python:3.12.3-slim-bookworm AS builder

# Set the working directory
WORKDIR /series-scraper

# Install git and git-lfs for cloning the repository
RUN apt-get update && apt-get install -y git git-lfs
RUN git lfs install

# Copy the current directory contents into the container at /
RUN git clone https://github.com/speedyconzales/series-scraper.git /series-scraper

COPY template.yml config.yml

# Stage 2: Final setup
FROM python:3.12.3-slim-bookworm AS final
LABEL org.opencontainers.image.source="https://github.com/speedyconzales/seroes-scraper"

WORKDIR /series-scraper

COPY --from=builder /series-scraper /series-scraper

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Install Chromium
RUN apt-get update && apt-get install -y chromium

# Install Chromium driver
RUN apt-get install -y chromium-driver

# Install FFmpeg
RUN apt-get install -y ffmpeg

# Set main.py as entrypoint
ENTRYPOINT ["python", "main.py"]
