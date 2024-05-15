import concurrent.futures
import os
import time
from urllib.request import HTTPError
from urllib.error import URLError

from src.argument_parser import ArgumentParser
from src.downloader import already_downloaded, create_new_download_thread
from src.episode_link_grabber import LanguageError, ProviderError
from src.logger import logger
from src.html_scraper import find_content_url, get_episodes, get_specials, get_episode_link


def check_active_threads(future_list, concurrent_downloads):
    logger.debug(f"{future_list}")
    active_futures = [future for future in future_list if future.running()]
    logger.debug(f"{active_futures}")
    logger.info(
        f"Max number of concurrent downloads = {concurrent_downloads} reached. Waiting for downloads to complete."
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
    burning_series,
):
    provider_episodes = []
    language_episodes = []
    future_list = []
    for episode in episodes:
        file_name = f"{season_path}/{content_name} - s{season:02}e{episode:0{3 if len(episodes) > 99 else 2}} - {language}.mp4"
        logger.debug(f"File name will be: {file_name}")
        if not already_downloaded(file_name):
            check_active_threads(future_list, concurrent_downloads)
            try:
                episode_link = get_episode_link(url, language, provider, season, episode, burning_series)
            except LanguageError:
                language_episodes.append(episode)
                continue
            except ProviderError:
                provider_episodes.append(episode)
                continue
            except (HTTPError, URLError) as message:
                logger.error(f"{message} while working on episode {episode} and provider {provider}")
                provider_episodes.append(episode)
                continue
            try:
                content_url = find_content_url(episode_link, provider)
            except Exception as message:
                logger.error(f"{message} while working on episode {episode} and provider {provider}")
                provider_episodes.append(episode)
                continue
            logger.debug(f"{provider} content URL is: {content_url}")
            future_list.append(create_new_download_thread(executor, content_url, file_name, episode, provider))
    return provider_episodes, language_episodes, future_list


def main():
    language, url, output_path, content_name, seasons, desired_episodes, provider, threads, burning_series = (
        ArgumentParser.language,
        ArgumentParser.url,
        ArgumentParser.output_path,
        ArgumentParser.content_name,
        ArgumentParser.seasons,
        ArgumentParser.episodes,
        ArgumentParser.provider,
        ArgumentParser.threads,
        ArgumentParser.burning_series,
    )

    logger.info("------------- Series-Scraper started ------------")

    os.makedirs(output_path, exist_ok=True)

    provider_list = ["VOE", "Vidoza", "Doodstream", "Streamtape"] if not provider else provider

    for season in seasons:
        season_path = f"{output_path}/Season {season:02}"
        os.makedirs(season_path, exist_ok=True)
        if season > 0 or burning_series:
            episodes = desired_episodes if desired_episodes else get_episodes(url, season, burning_series)
        else:
            episodes = desired_episodes if desired_episodes else get_specials(url)
        logger.info(f"Season {season} has {len(get_episodes(url, season, burning_series)) if season > 0 or burning_series else len(get_specials(url))} Episodes.")
        failed_episodes = []
        for provider in provider_list:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=threads
            ) as executor:
                provider_episodes, language_episodes, future_list = check_episodes(
                    threads,
                    executor,
                    season_path,
                    content_name,
                    url,
                    season,
                    episodes,
                    language,
                    provider,
                    burning_series,
                )
                failed_episodes.extend(language_episodes)
                for future in concurrent.futures.as_completed(future_list):
                    provider_episodes.append(
                        future.result()
                    ) if future.result() is not None else None
            if provider_episodes:
                logger.warning(f"The following episodes of season {season} couldn't be downloaded from provider '{provider}': {provider_episodes}")
                continue
            break
        logger.error(f"The following episodes of season {season} couldn't be downloaded in the desired language: {failed_episodes}") if failed_episodes else None
        logger.error(f"The following episodes of season {season} couldn't be downloaded from any of the supported providers: {provider_episodes}") if provider_episodes else None


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        time.sleep(1)
    logger.info("------------- Series-Scraper stopped ------------")
