import argparse
import os

from src.downloader import download_episode
from src.html_scraper import find_content_url

# WORK IN PROGRESS

ROOT = ""

def main():
    parser = argparse.ArgumentParser(description="cine.to-Scraper")

    parser.add_argument(
        "provider",
        choices=["VOE", "Streamtape", "Vidoza"],
        help="specify the provider of the content",
    )
    parser.add_argument("title", type=str, help="title of the content")
    parser.add_argument("url", type=str, help="url of the content")

    args = parser.parse_args()
    file_name = f"{args.title}.mp4"
    folder_name = os.path.join(ROOT, args.title)
    os.makedirs(folder_name, exist_ok=True)
    download_episode(
        find_content_url(args.url, args.provider),
        os.path.join(folder_name, file_name),
        0,
    )

if __name__ == "__main__":
    main()
