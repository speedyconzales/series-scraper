import concurrent.futures
import os
import time
from urllib.request import HTTPError
from urllib.error import URLError

from src.argument_parser import ArgumentParser
from src.downloader import ProviderError, already_downloaded, create_new_download_thread
from src.language import LanguageError
from src.logger import Logger as logger
from src.search_for_links import find_content_url, get_episodes, get_movies, get_redirect_link

MODULE_LOGGER_HEAD = "main.py -> "


def check_active_threads(future_list, concurrent_downloads):
    logger.debug(MODULE_LOGGER_HEAD + f"{future_list}")
    active_futures = [future for future in future_list if future.running()]
    logger.debug(MODULE_LOGGER_HEAD + f"{active_futures}")
    logger.info(
        MODULE_LOGGER_HEAD
        + f"Max number of concurrent downloads = {concurrent_downloads} reached. Waiting for downloads to complete."
    ) if len(active_futures) >= concurrent_downloads else None
    while len(active_futures) >= concurrent_downloads:
        active_futures = [future for future in future_list if future.running()]
        time.sleep(1)


def check_episodes(
    concurrent_downloads,
    executor,
    season_path,
    content_name,
    url,
    season,
    episodes,
    language,
    provider,
):
    provider_episodes = []
    language_episodes = []
    future_list = []
    for episode in episodes:
        file_name = f"{season_path}/{content_name} - s{season:02}e{episode:0{3 if len(episodes) > 99 else 2}} - {language}.mp4"
        logger.debug(MODULE_LOGGER_HEAD + "File name will be: " + file_name)
        if not already_downloaded(file_name):
            try:
                if season > 0:
                    redirect_link, provider = get_redirect_link(
                        f"{url}staffel-{season}/episode-{episode}", language, provider, season, episode
                    )
                else:
                    redirect_link, provider = get_redirect_link(
                        f"{url}filme/film-{episode}", language, provider, season, episode
                    )
            except LanguageError:
                language_episodes.append(episode)
                continue
            except ProviderError:
                provider_episodes.append(episode)
                continue
            except [HTTPError, URLError] as message:
                logger.error(
                    MODULE_LOGGER_HEAD
                    + f"{message} while working on episode {episode} and provider {provider}"
                )
                provider_episodes.append(episode)
                continue
            try:
                content_url = find_content_url(redirect_link, provider)
            except Exception as message:
                logger.error(
                    MODULE_LOGGER_HEAD
                    + f"{message} while working on episode {episode} and provider {provider}"
                )
                provider_episodes.append(episode)
                continue
            logger.debug(
                MODULE_LOGGER_HEAD + f"{provider} content URL is: {content_url}"
            )
            check_active_threads(future_list, concurrent_downloads)
            future_list.append(
                create_new_download_thread(executor, content_url, file_name, episode)
            )
    return provider_episodes, language_episodes, future_list


def main():
    language, url, output_path, content_name, seasons, desired_episode, threads = (
        ArgumentParser.args.language,
        ArgumentParser.url,
        ArgumentParser.output_path,
        ArgumentParser.content_name,
        ArgumentParser.seasons,
        ArgumentParser.episodes,
        ArgumentParser.threads,
    )

    logger.info("------------- AnimeSerienScraper started ------------")

    os.makedirs(output_path, exist_ok=True)

    provider_list = ["VOE", "VOE", "Vidoza", "Streamtape"]

    for season in seasons:
        season_path = f"{output_path}/Season {season:02}"
        os.makedirs(season_path, exist_ok=True)
        if season > 0:
            pending_episodes = (
            get_episodes(url, season) if desired_episode == 0 else desired_episode
            )
        else:
            pending_episodes = get_movies(url)
        logger.info(
            MODULE_LOGGER_HEAD
            + f"Season {season} has {len(get_episodes(url,season)) if season > 0 else len(get_movies(url))} Episodes."
        )
        failed_episodes = []
        for provider in provider_list:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=threads
            ) as executor:
                pending_episodes, language_episodes, future_list = check_episodes(
                    threads,
                    executor,
                    season_path,
                    content_name,
                    url,
                    season,
                    pending_episodes,
                    language,
                    provider,
                )
                failed_episodes.extend(language_episodes)
                for future in concurrent.futures.as_completed(future_list):
                    pending_episodes.append(
                        future.result()
                    ) if future.result() is not None else None
            if pending_episodes:
                logger.warning(
                    MODULE_LOGGER_HEAD
                    + f"The following episodes of season {season} couldn't be downloaded from provider '{provider}': {pending_episodes}"
                )
                continue
            break
        logger.error(
            MODULE_LOGGER_HEAD
            + f"The following episodes of season {season} couldn't be downloaded in the desired language: {failed_episodes}"
        ) if failed_episodes else None
        logger.error(
            MODULE_LOGGER_HEAD
            + f"The following episodes of season {season} couldn't be downloaded from any of the supported providers: {pending_episodes}"
        ) if pending_episodes else None


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    logger.info("------------- AnimeSerienScraper stopped ------------")
