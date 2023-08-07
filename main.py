import os
import time
import concurrent.futures

from src.search_for_links import get_episodes, get_redirect_link, find_content_url
from src.downloader import already_downloaded, create_new_download_thread
from src.downloader import ProviderError
from src.language import LanguageError
from src.logger import Logger as logger
from src.argument_parser import ArgumentParser


MODULE_LOGGER_HEAD = "main.py -> "


def check_active_threads(future_list, concurrent_downloads):
    logger.debug(MODULE_LOGGER_HEAD + f"{future_list}")
    active_futures = [future for future in future_list if future.running()]
    logger.debug(MODULE_LOGGER_HEAD + f"{active_futures}")
    logger.info(MODULE_LOGGER_HEAD + f"Max number of concurrent downloads = {concurrent_downloads} reached. Waiting for downloads to complete.") if len(active_futures) >= concurrent_downloads else None
    while len(active_futures) >= concurrent_downloads:
        active_futures = [future for future in future_list if future.running()]
        time.sleep(1)


def check_episodes(concurrent_downloads, executor, season_path, content_name, url, season, episodes, language, provider):
    provider_episodes = []
    language_episodes =[]
    future_list = []
    for episode in episodes:
        file_name = "{}/{} - s{:02}e{:0{width}} - {}.mp4".format(season_path, content_name, season, episode, language, width=3 if len(episodes) > 99 else 2)
        logger.debug(MODULE_LOGGER_HEAD + "File name will be: " + file_name)
        if not already_downloaded(file_name):
            try:
                redirect_link, provider = get_redirect_link(f"{url}staffel-{season}/episode-{episode}", language, provider)
            except LanguageError:
                language_episodes.append(episode)
                continue
            except ProviderError:
                provider_episodes.append(episode)
                continue
            content_url = find_content_url(redirect_link, provider)
            logger.debug(MODULE_LOGGER_HEAD + f"{provider} content URL is: {content_url}")
            check_active_threads(future_list, concurrent_downloads)
            future_list.append(create_new_download_thread(executor, content_url, file_name, episode))
    return provider_episodes, language_episodes, future_list


def main(concurrent_downloads=2):
    language, url, output_path, content_name, seasons, desired_episode = ArgumentParser.args.language, ArgumentParser.url, ArgumentParser.output_path, ArgumentParser.content_name, ArgumentParser.seasons, ArgumentParser.episodes

    logger.info("------------- AnimeSerienScraper started ------------")

    os.makedirs(output_path, exist_ok=True)

    provider_list = ["VOE", "Streamtape", "Vidoza"]

    for season in seasons:
        season_path = f"{output_path}/Season {season:02}"
        os.makedirs(season_path, exist_ok=True)
        pending_episodes = get_episodes(url, season) if desired_episode == 0 else desired_episode
        logger.info(MODULE_LOGGER_HEAD + f"Season {season} has {len(get_episodes(url,season))} Episodes.")
        failed_episodes = []
        for provider in provider_list:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_downloads) as executor:
                pending_episodes, language_episodes, future_list = check_episodes(concurrent_downloads, executor, season_path, content_name, url, season, pending_episodes, language, provider)
                failed_episodes.extend(language_episodes)
                print("FATHER I SEE YOU")
                for future in concurrent.futures.as_completed(future_list):
                    print(f"MOTHER {future.result()}")
                    pending_episodes.append(future.result()) if future.result() is not None else None
            if pending_episodes:
                logger.warning(MODULE_LOGGER_HEAD + f"The following episodes of season {season} couldn't be downloaded from provider '{provider}':\n{pending_episodes}")
                continue
            else:
                break
        logger.error(MODULE_LOGGER_HEAD + f"The following episodes of season {season} couldn't be downloaded in the desired language:\n{failed_episodes}") if failed_episodes else None
        logger.error(MODULE_LOGGER_HEAD + f"The following episodes of season {season} couldn't be downloaded from any of the supported provider:\n{pending_episodes}") if pending_episodes else None
        


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    logger.info("------------- AnimeSerienScraper stopped ------------")
