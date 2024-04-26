import argparse
import yaml

from src.search_for_links import get_season


class ArgumentParser:
    with open('config.yml', 'r') as yaml_file:
        config = yaml.safe_load(yaml_file)
    anime_path = config['anime_folder']
    serie_path = config['serien_folder']
    type = {
        "serie": {
            "path": serie_path,
            "url": "https://s.to",
        },
        "anime": {
            "path": anime_path,
            "url": "https://aniworld.to"
        },
    }

    parser = argparse.ArgumentParser(description="S.to - Scraper")

    parser.add_argument(
        "type", choices=["serie", "anime"], help="specify the type of the content"
    )
    parser.add_argument("name", type=str, help="name of the content")
    parser.add_argument("language", type=str, help="desired language of the content")

    parser.add_argument("-s", "--season", type=int, help="specify the season")
    parser.add_argument("-e", "--episode", type=int, help="specify the episode")
    parser.add_argument("-t", "--threads", type=int, help="specify the number of threads")

    args = parser.parse_args()

    if args.episode and not args.season:
        parser.error("You have to specify a season in order to specify an episode")

    threads = args.threads if args.threads is not None else 2
    url = f"{type[args.type]['url']}/{args.type}/stream/{args.name}/"
    content_name = args.name.replace("-", " ").title()
    output_path = f"{type[args.type]['path']}/{content_name}"
    seasons = [args.season] if args.season is not None else get_season(url)
    episodes = [args.episode] if args.episode is not None else None
