import argparse
from .search_for_links import get_season

class ArgumentParser:
    parser = argparse.ArgumentParser(description="S.to - Scraper")
    
    parser.add_argument("type", choices=["serie","anime"], help="specify the type of the content")
    parser.add_argument("name", type=str, help="name of the content")
    parser.add_argument("language", type=str, help="desired language of the content")
    
    parser.add_argument("-s", "--season", type=int, help="specify the season")
    parser.add_argument("-e", "--episode", type=int, help="specify the episode")
    
    args = parser.parse_args()
    
    if args.episode and not args.season:
        parser.error("You have to specify a season in order to specify an episode")

    site_url = {"serie": "https://s.to", # maybe you need another dns to be able to use this site
                "anime": "https://aniworld.to"}
    url = "{}/{}/stream/{}/".format(site_url[args.type], args.type, args.name)
    output_path = args.name.replace("-"," ").title()
    seasons = [args.season] if args.season else get_season(url)
    episodes = [args.episode] if args.episode else 0
