import urllib.request

from bs4 import BeautifulSoup

from src.logger import logger


class ProviderError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class LanguageError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def get_bs_href_by_language(url, language, provider, season, episode):
    bs_language_mapping = {
            "Deutsch": "de",
            "Ger-Sub": "des",
            "English": "jps"
        }
    html_response = urllib.request.urlopen(f"{url}{season}/{bs_language_mapping.get(language)}")
    soup = BeautifulSoup(html_response, "html.parser")
    episode_has_language = False
    links = soup.find_all('i', class_='hoster')
    for link in links:
        href = str(link.parent.get("href"))
        if f"{season}/{episode}" in href:
            episode_has_language = True
            parts = href.split("/")
            link_provider = parts[-1]
            if link_provider == provider:
                return "/" + href
    if not episode_has_language:
        raise LanguageError(logger.error(f"Episode {episode} in season {season} does not support language '{language}'"))
    raise ProviderError(
        logger.error(f"Provider '{provider} does not have a download for episode '{episode}' season '{season}' in language'{language}'")
    )


def get_href_by_language(html_response, language, provider, season, episode):
    soup = BeautifulSoup(html_response, "html.parser")
    language_mapping = {
        "Deutsch": 1,
        "Ger-Sub": 3,
        "English": 2,
    }
    matching_li_elements = soup.find_all("li", {"data-lang-key": language_mapping.get(language)})
    if not matching_li_elements:
        raise LanguageError(logger.error(f"Episode {episode} in season {season} does not support language '{language}'."))
    provider_li_element = next(
        (
            li_element
            for li_element in matching_li_elements
            if li_element.find("h4").get_text() == provider
        ),
        None,
    )
    if provider_li_element:
        href = provider_li_element.get("data-link-target", "")
        return href
    raise ProviderError(
        logger.error(f"Provider '{provider} does not have a download for episode '{episode}' season '{season}' in language'{language}'")
    )
