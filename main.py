import os
import time
import threading

from src.search_for_links import find_content_url, get_redirect_link_by_provider, get_episodes
from src.downloader import create_new_download_thread, already_downloaded
from src.language import LanguageError, ProviderError
from src.logger import Logger as logger
from src.argument_parser import ArgumentParser

MODULE_LOGGER_HEAD = "main.py -> "


def main(concurrent_downloads=5):
    
    language, url, output_path, seasons, desired_episode = ArgumentParser.args.language, ArgumentParser.url, ArgumentParser.output_path, ArgumentParser.seasons, ArgumentParser.episodes

    logger.info("------------- AnimeSerienScraper started ------------")
    
    os.makedirs(output_path, exist_ok=True)

    thread_semaphore = threading.Semaphore(concurrent_downloads)
    active_threads: list[threading.Thread] = []

    for season in seasons:
        season_path = f"{output_path}/Season {season:02}"
        os.makedirs(season_path, exist_ok=True)
        episodes = get_episodes(url, season) if desired_episode == 0 else desired_episode
        logger.info(MODULE_LOGGER_HEAD + "Season {} has {} Episodes.".format(season, len(get_episodes(url,season))))

        for episode in episodes:
            file_name = "{}/{} - s{:02}e{:0{width}} - {}.mp4".format(season_path, output_path, season, episode, language, width=3 if len(episodes) > 99 else 2)
            logger.info(MODULE_LOGGER_HEAD + "File name will be: " + file_name)
            if not already_downloaded(file_name):
                episode_link = url + "staffel-{}/episode-{}".format(season, episode)
                try:
                    redirect_link, provider = get_redirect_link_by_provider(episode_link, language)
                except (LanguageError, ProviderError):
                    continue
                content_url = find_content_url(redirect_link, provider)
                logger.debug(MODULE_LOGGER_HEAD + "{} content URL is: ".format(provider) + content_url)
                create_new_download_thread(thread_semaphore, active_threads, content_url, file_name, provider)
                while len(active_threads) >= concurrent_downloads:
                    time.sleep(1)
                    active_threads = [t for t in active_threads if t.is_alive()]

    for thread in active_threads:
        thread.join()



if __name__ == "__main__":
    main()
    logger.info("------------- AnimeSerienScraper stopped ------------")
