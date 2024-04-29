import argparse
import yaml

from urllib.parse import urlparse
from src.html_scraper import get_seasons


class ArgumentParser:
    def is_valid_url(url):
        url = urlparse(url)
        if all((url.hostname, url.path)):
            if url.hostname in ["bs.to", "aniworld.to", "s.to"]:
                return url
            raise argparse.ArgumentTypeError('Site not supported. Please create a feature request on GitHub')
        raise argparse.ArgumentTypeError('Malformed url. Please provide a valid url')

    with open('config.yml', 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    anime_path = config['anime_folder']
    series_path = config['series_folder']

    parser = argparse.ArgumentParser(description="Series-Scraper")

    parser.add_argument(
        "type", choices=["serie", "anime"], help="specify the type of the content"
    )
    parser.add_argument("url", type=is_valid_url, help="url of the series")
    parser.add_argument("language", choices=["Deutsch", "Ger-Sub", "Eng-Sub", "English"], help="desired language of the content")

    parser.add_argument("-s", "--season", type=int, help="specify the season")
    parser.add_argument("-e", "--episode", type=int, help="specify the episode")
    parser.add_argument("-t", "--threads", type=int, help="specify the number of threads or concurrent downloads")

    args = parser.parse_args()

    if args.episode and args.season is None:
        parser.error("You have to specify a season in order to specify an episode")

    threads = args.threads if args.threads is not None else 2
    if args.url.hostname == "bs.to":
        burning_series = True
        content_name = args.url.path.split("/")[2]
        url = f"https://bs.to/serie/{content_name}/"
    else:
        burning_series = False
        try:
            content_name = args.url.path.split("/")[3]
        except IndexError:
            parser.error("Malformed url. The name of the series needs to be in the url")
        url = f"https://{args.url.hostname}/{args.type}/stream/{content_name}/"
    language = args.language
    content_name = content_name.replace("-", " ").title()
    if args.type == "anime":
        output_path = f"{anime_path}/{content_name}"
    else:
        output_path = f"{series_path}/{content_name}"
    seasons = [args.season] if args.season is not None else get_seasons(url, burning_series)
    episodes = [args.episode] if args.episode else 0
