import re
import sys
import urllib.request
import undetected_chromedriver as uc

from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.episode_link_grabber import get_href_by_language, get_bs_href_by_language
from src.logger import Logger as logger


MODULE_LOGGER_HEAD = "search_for_links.py -> "
VOE_PATTERNS = [re.compile(r"'hls': '(?P<url>.+)'"),
                re.compile(r'prompt\("Node",\s*"(?P<url>[^"]+)"')]
STREAMTAPE_PATTERN = re.compile(
    r"get_video\?id=[^&\'\s]+&expires=[^&\'\s]+&ip=[^&\'\s]+&token=[^&\'\s]+\'"
)


def get_episode_link(url, language, provider, season, episode, burning_series):
    if burning_series:
        html_response = urllib.request.urlopen(f"{url}{season}/{language}")
        href_value = get_bs_href_by_language(html_response, language, provider, season, episode)
    else:
        if season > 0:
            html_response = urllib.request.urlopen(f"{url}staffel-{season}/episode-{episode}")
        else:
            html_response = urllib.request.urlopen(f"{url}filme/film-{episode}")
        href_value = get_href_by_language(html_response, language, provider, season, episode)
    parsed_url = urlsplit(url)
    base_url = urlunsplit((parsed_url.scheme, parsed_url.hostname, "", "", ""))
    link_to_episode = base_url + href_value
    if burning_series:
        link_to_episode = find_bs_link_to_episode(link_to_episode, provider)
    logger.debug(MODULE_LOGGER_HEAD + "Link to episode is: " + link_to_episode)
    return link_to_episode


def get_voe_content_link_with_selenium(provider_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(provider_url)
    voe_play_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'voe-play'))
    )
    voe_play_div.click()
    video_in_media_provider = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'media-provider video source:nth-of-type(2)'))
    )
    content_link = video_in_media_provider.get_attribute('src')
    driver.quit()
    return content_link


def find_content_url(url, provider):
    html_page = urllib.request.urlopen(url)
    if provider == "Vidoza":
        soup = BeautifulSoup(html_page, features="html.parser")
        content_link = soup.find("source").get("src")
    elif provider == "VOE":
        def content_link_is_not_valid(content_link):
            return content_link is None or not content_link.startswith("https://")
        html_page = html_page.read().decode("utf-8")
        for VOE_PATTERN in VOE_PATTERNS:
            content_link = VOE_PATTERN.search(html_page).group("url")
            if content_link_is_not_valid(content_link):
                continue
            else:
                return content_link
        content_link = get_voe_content_link_with_selenium(url)
        if content_link_is_not_valid(content_link):
            logger.error(MODULE_LOGGER_HEAD + "Failed to find the video links of provider VOE. Exiting...")
            sys.exit(1)
    elif provider == "Streamtape":
        content_link = STREAMTAPE_PATTERN.search(html_page.read().decode("utf-8"))
        if content_link is None:
            return find_content_url(url, provider)
        content_link = "https://" + provider + ".com/" + content_link.group()[:-1]
    logger.debug(
        MODULE_LOGGER_HEAD
        + f"Found the following video link of {provider}: {content_link}"
    )
    return content_link
    

def find_bs_link_to_episode(url, provider):
    options = uc.ChromeOptions()
    # headless is currently not working with undetected_chromedriver
    # and there are captchas you have to solve
    #options.add_argument("--headless")
    driver = uc.Chrome(options=options)
    driver.get(url)
    cookie = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.cc-compliance a'))
    )
    cookie.click()
    play_div = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '.hoster-player .play'))
    )
    play_div.click()
    if provider == "VOE":
        video_in_media_provider = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.hoster-player a'))
        )
        content_link = video_in_media_provider.get_attribute('href')
    elif provider in ["Streamtape", "Vidoza"]:
        video_in_media_provider = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.hoster-player iframe'))
        )
        content_link = video_in_media_provider.get_attribute('src')
    else:
        logger.error(MODULE_LOGGER_HEAD + "No supported hoster available for this episode")
    driver.quit()
    return content_link


def get_seasons(url_path, burning_series=False) -> list:
    logger.debug(MODULE_LOGGER_HEAD + "Site URL is: " + url_path)
    counter_seasons = 1
    html_page = urllib.request.urlopen(url_path, timeout=50)
    soup = BeautifulSoup(html_page, features="html.parser")
    if burning_series:
        for li in soup.findAll("li"):
            season = str(li.get("class"))
            if f"s{counter_seasons}" in season:
                counter_seasons += 1
    else:
        for link in soup.findAll("a"):
            href = str(link.get("href"))
            if f"/staffel-{counter_seasons}" in href:
                counter_seasons += 1
    seasons = [i for i in range(1, counter_seasons)]
    return seasons


def get_episodes(url_path, season, burning_series=False) -> list:
    counter_episodes = 1
    if burning_series:
        url = f"{url_path}{season}/"
        html_page = urllib.request.urlopen(url, timeout=50)
        soup = BeautifulSoup(html_page, features="html.parser")
        for link in soup.findAll("a"):
            href = str(link.get("href"))
            if f"{season}/{counter_episodes}" in href:
                counter_episodes += 1
    else:
        url = f"{url_path}staffel-{season}/"
        html_page = urllib.request.urlopen(url, timeout=50)
        soup = BeautifulSoup(html_page, features="html.parser")
        for link in soup.findAll("a"):
            href = str(link.get("href"))
            if f"/staffel-{season}/episode-{counter_episodes}" in href:
                counter_episodes += 1
    episodes = [i for i in range(1, counter_episodes)]
    return episodes


def get_specials(url_path) -> list:
    url = f"{url_path}filme/"
    counter_movies = 1
    html_page = urllib.request.urlopen(url, timeout=50)
    soup = BeautifulSoup(html_page, features="html.parser")
    for link in soup.findAll('a'):
        movie = str(link.get("href"))
        if f"/filme/film-{counter_movies}" in movie:
            counter_movies += 1
    movies = [i for i in range(1, counter_movies)]
    return movies
