import os
import re
import sys
import urllib.request
import zipfile

from base64 import b64decode
from random import choices
from string import ascii_letters, digits
from time import time
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup
from selenium import webdriver
from seleniumbase import SB
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService

from src.episode_link_grabber import get_href_by_language, get_bs_href_by_language
from src.logger import logger

DOODSTREAM_PATTERN = re.compile(r"/pass_md5/[\w-]+/(?P<token>[\w-]+)")
VOE_PATTERNS = [re.compile(r"'hls': '(?P<url>.+)'"),
                re.compile(r'prompt\("Node",\s*"(?P<url>[^"]+)"')]
STREAMTAPE_PATTERN = re.compile(r"get_video\?id=[^&\'\s]+&expires=[^&\'\s]+&ip=[^&\'\s]+&token=[^&\'\s]+\'")
SPEEDFILES_PATTERN = re.compile(r"var _0x5opu234 = \"(?P<content>.*?)\";")

def get_episode_link(url, language, provider, season, episode, burning_series):
    if burning_series:
        href_value = get_bs_href_by_language(url, language, provider, season, episode)
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
    logger.debug(f"Link to episode is: {link_to_episode}")
    return link_to_episode


def get_voe_content_link_with_selenium(provider_url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--no-sandbox")
    chrome_driver_path = "/usr/bin/chromedriver"
    if os.path.exists(chrome_driver_path):
        chrome_service = ChromeService(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)
    driver.get(provider_url)
    decoded_html = urllib.request.urlopen(driver.current_url).read().decode("utf-8")
    content_link = voe_pattern_search(decoded_html)
    if content_link is not None:
        driver.quit()
        return content_link
    voe_play_div = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Play']"))
    )
    voe_play_div.click()
    video_in_media_provider = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'media-provider video source'))
    )
    content_link = video_in_media_provider.get_attribute('src')
    driver.quit()
    return content_link

def voe_pattern_search(decoded_html):
    for VOE_PATTERN in VOE_PATTERNS:
        match = VOE_PATTERN.search(decoded_html)
        if match is None:
            continue
        content_link = match.group("url")
        if content_link_is_not_valid(content_link):
            try:
                content_link = b64decode(content_link).decode()
                if content_link_is_not_valid(content_link):
                    continue
                return content_link
            except Exception:
                pass
            continue
        return content_link

def content_link_is_not_valid(content_link):
    return content_link is None or not content_link.startswith("https://")
    
def find_content_url(url, provider):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    req = urllib.request.Request(url, headers=headers)
    decoded_html = urllib.request.urlopen(req).read().decode("utf-8")
    if provider == "Vidoza":
        soup = BeautifulSoup(decoded_html, features="html.parser")
        content_link = soup.find("source").get("src")
    elif provider == "VOE":
        content_link = voe_pattern_search(decoded_html)
        if content_link is None:
            content_link = get_voe_content_link_with_selenium(url)
        if content_link_is_not_valid(content_link):
            logger.critical("Failed to find the video links of provider VOE. Exiting...")
            sys.exit(1)
    elif provider == "Streamtape":
        content_link = STREAMTAPE_PATTERN.search(decoded_html)
        if content_link is None:
            return find_content_url(url, provider)
        content_link = "https://" + provider + ".com/" + content_link.group()[:-1]
    elif provider == "Doodstream":
        pattern_match = DOODSTREAM_PATTERN.search(decoded_html)
        pass_md5 = pattern_match.group()
        token = pattern_match.group("token")
        headers['Referer'] = 'https://d0000d.com/'
        req = urllib.request.Request(f"https://d0000d.com{pass_md5}", headers=headers)
        response_page = urllib.request.urlopen(req)
        content_link = f"{response_page.read().decode('utf-8')}{''.join(choices(ascii_letters + digits, k=10))}?token={token}&expiry={int(time() * 1000)}"
    elif provider == "SpeedFiles":
        match = SPEEDFILES_PATTERN.search(decoded_html)
        content = match.group("content")
        content = b64decode(content).decode()
        content = content.swapcase()
        content = ''.join(reversed(content))
        content = b64decode(content).decode()
        content = ''.join(reversed(content))
        next_content = ""
        for i in range(0, len(content), 2):
            next_content += chr(int(content[i:i + 2], 16))
        content_link = ""
        for char in next_content:
            content_link += chr(ord(char) - 3)
        content_link = content_link.swapcase()
        content_link = ''.join(reversed(content_link))
        content_link = b64decode(content_link).decode()
    logger.debug(f"Found the following video link of {provider}: {content_link}")
    return content_link


def find_and_unzip_crx():
    src_path = os.path.dirname(os.path.abspath(__file__))
    extensions_path = os.path.join(src_path, "extensions")
    for root, dirs, files in os.walk(extensions_path):
        for file in files:
            if file.endswith('.crx'):
                extract_path = os.path.join(extensions_path, os.path.splitext(os.path.basename(file))[0])
                os.makedirs(extract_path, exist_ok=True)
                if not os.listdir(extract_path):
                    crx_file_path = os.path.join(root, file)
                    with zipfile.ZipFile(crx_file_path, 'r') as zip_ref:
                        zip_ref.extractall(extract_path)
                    logger.debug(f"Extracted {file} in {extract_path}")
                break
    return extract_path


def find_bs_link_to_episode(url, provider):
    with SB(uc=True, headless2=True, extension_dir=find_and_unzip_crx()) as sb:
        sb.open(url)
        sb.click('.cc-compliance a')
        sb.click('.hoster-player .play')
        if provider == "VOE":
            content_link = sb.wait_for_element_visible('.hoster-player a', timeout=240).get_attribute("href")
        elif provider == "Doodstream":
            sb.switch_to_tab(1, timeout=240)
            html = sb.get_page_source()
            soup = BeautifulSoup(html, features="html.parser")
            iframe_src = soup.find("iframe").get("src")
            content_link = f"https://d000d.com{iframe_src}"
        elif provider in ["Streamtape", "Vidoza"]:
            content_link = sb.wait_for_element_visible('.hoster-player iframe', timeout=240).get_attribute("src")
        else:
            logger.error("No supported hoster available for this episode")
    return content_link


def get_seasons(url_path, burning_series=False) -> list:
    logger.debug(f"Site URL is: {url_path}")
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
