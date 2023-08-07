import re
import urllib.request

from urllib.error import URLError
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit
from .language import get_href_by_language
from .logger import Logger as logger

MODULE_LOGGER_HEAD = "search_for_links.py -> "

VOE_PATTERN = re.compile(r"'hls': '(?P<url>.+)'")
STREAMTAPE_PATTERN = re.compile(r'get_video\?id=[^&\'\s]+&expires=[^&\'\s]+&ip=[^&\'\s]+&token=[^&\'\s]+\'')


def get_redirect_link(episode_link, language, provider):
    html_response = urllib.request.urlopen(episode_link)
    href_value = get_href_by_language(html_response, language, provider)
    parsed_url = urlsplit(episode_link)
    base_url = urlunsplit((parsed_url.scheme, parsed_url.netloc, '', '', ''))
    link_to_redirect = base_url + href_value
    logger.debug(MODULE_LOGGER_HEAD + "Link to redirect is: " + link_to_redirect)
    return link_to_redirect, provider
     

def find_content_url(url, provider):
    try:
        html_page = urllib.request.urlopen(url)
    except URLError as e:
        logger.warning(MODULE_LOGGER_HEAD + f"{e}")
        logger.info(MODULE_LOGGER_HEAD + "Trying again...")
        return find_content_url(url, provider)
    if provider == "Vidoza":
        soup = BeautifulSoup(html_page, features="html.parser")
        content_link = soup.find("source").get("src")
    elif provider == "VOE":
        content_link = VOE_PATTERN.search(html_page.read().decode('utf-8')).group("url")
    elif provider == "Streamtape":
        content_link = STREAMTAPE_PATTERN.search(html_page.read().decode('utf-8'))
        if content_link is None:
            return find_content_url(url, provider)
        content_link = "https://" + provider + ".com/" + content_link.group()[:-1]
        logger.debug(MODULE_LOGGER_HEAD + f"This is the found video link of {provider}: {content_link}")
    return content_link

def get_season(url_path) -> list:
    logger.debug(MODULE_LOGGER_HEAD + "Site URL is: " + url_path)
    counter_seasons = 1
    html_page = urllib.request.urlopen(url_path, timeout=50)
    soup = BeautifulSoup(html_page, features="html.parser")
    for link in soup.findAll('a'):
        href = str(link.get("href"))
        if f"/staffel-{counter_seasons}" in href:
            counter_seasons += 1
    seasons = [i for i in range(1, counter_seasons)]
    return seasons


def get_episodes(url_path, season) -> list:
    url = "{}staffel-{}/".format(url_path, season)
    counter_episodes = 1
    html_page = urllib.request.urlopen(url, timeout=50)
    soup = BeautifulSoup(html_page, features="html.parser")
    for link in soup.findAll('a'):
        href = str(link.get("href"))
        if f"/staffel-{season}/episode-{counter_episodes}" in href:
            counter_episodes += 1
    episodes = [i for i in range(1, counter_episodes)]
    return episodes