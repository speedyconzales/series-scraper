import argparse

from src.search_for_links import get_season


class ArgumentParser:
    type = {
        "serie": {
            "path": "Serien",
            "url": "https://s.to",
        },  # maybe you need another dns to be able to use this site
        "anime": {"path": "Animes", "url": "https://aniworld.to"},
    }

    parser = argparse.ArgumentParser(description="S.to - Scraper")

    parser.add_argument(
        "type", choices=["serie", "anime"], help="specify the type of the content"
    )
    parser.add_argument("name", type=str, help="name of the content")
    parser.add_argument("language", type=str, help="desired language of the content")

    parser.add_argument("-s", "--season", type=int, help="specify the season")
    parser.add_argument("-e", "--episode", type=int, help="specify the episode")

    args = parser.parse_args()

    if args.episode and not args.season:
        parser.error("You have to specify a season in order to specify an episode")

    url = f"{type[args.type]['url']}/{args.type}/stream/{args.name}/"
    content_name = args.name.replace("-", " ").title()
    output_path = f"{type[args.type]['path']}/{content_name}"
    seasons = [args.season] if args.season else get_season(url)
    episodes = [args.episode] if args.episode else 0
