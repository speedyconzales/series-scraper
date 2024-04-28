import argparse
import yaml

from urllib.parse import urlsplit
from src.html_scraper import get_seasons


class ArgumentParser:
    with open('config.yml', 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    anime_path = config['anime_folder']
    series_path = config['series_folder']

    parser = argparse.ArgumentParser(description="Series-Scraper")

    parser.add_argument(
        "type", choices=["serie", "anime"], help="specify the type of the content"
    )
    parser.add_argument("url", type=str, help="url of the series")
    parser.add_argument("language", choices=["Deutsch", "Ger-Sub", "English"], help="desired language of the content")

    parser.add_argument("-s", "--season", type=int, help="specify the season")
    parser.add_argument("-e", "--episode", type=int, help="specify the episode")
    parser.add_argument("-t", "--threads", type=int, help="specify the number of threads or concurrent downloads")

    args = parser.parse_args()

    if args.episode and args.season is None:
        parser.error("You have to specify a season in order to specify an episode")

    threads = args.threads if args.threads is not None else 2
    url_split = urlsplit(args.url)
    if url_split.hostname == "bs.to":
        burning_series = True
        content_name = url_split.path.split("/")[2]
        url = f"https://bs.to/serie/{content_name}/"
        bs_language_mapping = {
            "Deutsch": "de",
            "Ger-Sub": "des",
            "English": "jps"
        }
        language = bs_language_mapping.get(args.language)
    else:
        burning_series = False
        content_name = url_split.path.split("/")[3]
        url = f"https://{url_split.hostname}/{args.type}/stream/{content_name}/"
        language = args.language
    content_name = content_name.replace("-", " ").title()
    if args.type == "anime":
        output_path = f"{anime_path}/{content_name}"
    else:
        output_path = f"{series_path}/{content_name}"
    seasons = [args.season] if args.season is not None else get_seasons(url, args.burning_series)
    episodes = [args.episode] if args.episode else 0
