import os
import time
import argparse

from src.search_for_links import find_content_url, get_redirect_link_by_provider, get_season, get_episodes
from src.downloader import create_new_download_thread, already_downloaded
from src.language import LanguageError
from src.logger import Logger as logger

MODULE_LOGGER_HEAD = "main.py -> "


def setup_arguments(site_url):
    parser = argparse.ArgumentParser(description="S.to - Scraper")
    
    parser.add_argument("type", choices=["serie","anime"], help="specify the type of the content")
    parser.add_argument("name", type=str, help="name of the content")
    parser.add_argument("language", type=str, help="desired language of the content")
    
    parser.add_argument("-s", "--season", type=int, help="specify the season")
    parser.add_argument("-e", "--episode", type=int, help="specify the episode")
    
    args = parser.parse_args()
    
    if args.episode and not args.season:
        parser.error("You have to specify a season in order to specify an episode")

    url = "{}/{}/stream/{}/".format(site_url[args.type], args.type, args.name)
    output_path = args.name.replace("-"," ").title()
    seasons = [args.season] if args.season else get_season(url)
    episodes = [args.episode] if args.episode else 0

    return args.language,url,output_path,seasons,episodes


def main(ddos_start_value, ddos_protection_number, ddos_wait_timer, site_url):
    
    language,url,output_path,seasons,desired_episode = setup_arguments(site_url)

    logger.info("------------- AnimeSerienScraper started ------------")

    os.makedirs(output_path, exist_ok=True)

    for season in seasons:
        season_path = f"{output_path}/Season {season:02}"
        os.makedirs(season_path, exist_ok=True)
        episodes = get_episodes(url, season) if desired_episode == 0 else desired_episode
        logger.info(MODULE_LOGGER_HEAD + "Season {} has {} Episodes.".format(season, len(episodes)))

        for episode in episodes:
            file_name = "{}/{} - s{:02}e{:02} - {}.mp4".format(season_path, output_path, season, episode, language)
            logger.info(MODULE_LOGGER_HEAD + "File name will be: " + file_name)
            if not already_downloaded(file_name):
                episode_link = url + "staffel-{}/episode-{}".format(season, episode)
                try:
                    redirect_link, provider = get_redirect_link_by_provider(episode_link, language)
                except LanguageError:
                    continue
                if ddos_start_value < ddos_protection_number:
                    logger.debug(MODULE_LOGGER_HEAD + "Entered DDOS var check and starting new downloader.")
                    ddos_start_value += 1
                else:
                    logger.info(MODULE_LOGGER_HEAD + "Started {} Downloads. Waiting for {} Seconds to not trigger DDOS"
                                                    "Protection.".format(ddos_protection_number, ddos_wait_timer))
                    time.sleep(ddos_wait_timer)
                    ddos_start_value = 1
                content_url = find_content_url(redirect_link, provider)
                logger.debug(MODULE_LOGGER_HEAD + "{} content URL is: ".format(provider) + content_url)
                create_new_download_thread(content_url, file_name, provider)


if __name__ == "__main__":
    site_url = {"serie": "https://s.to", # maybe you need another dns to be able to use this site
                "anime": "https://aniworld.to"}
    try:
        main(0, 5, 60, site_url)
    except KeyboardInterrupt:
        logger.info("-----------------------------------------------------------")
        logger.info("            AnimeSerienScraper Stopped")
        logger.info("-----------------------------------------------------------")
        logger.info("Downloads may still be running. Please dont close this Window until its done.")
        logger.info("You will know its done once you see your primary prompt string. Example: C:\\XXX or username@hostname:")
