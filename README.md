# Series-Scraper

## Supported Sites
- headless and completely automated scraping of the following sites:
  - [aniworld.to](https://aniworld.to)
  - [s.to](https://s.to)
  - [bs.to](https://bs.to) -> uses headless browser for scraping and solving captchas

## Supported Hosters
- [VOE](https://voe.sx)
- [Vidoza](https://vidoza.net)
- [Streamtape](https://streamtape.com)

## Dependencies

1. install [ffmpeg](https://ffmpeg.org/download.html) and make sure it is in PATH -> `ffmpeg -version`
2. install [chrome](https://www.google.com/chrome/) or [chromium](https://www.chromium.org/getting-involved/download-chromium/)
3. install requirements via `pipenv` and Pipfile OR create a virtual environment and install them via `pip` and requirements.txt
4. copy and rename `template.yml` to `config.yml` and fill in the required folder paths for the respective type of the content
5. if you want to download from [bs.to](?plain=1#L7) you need to make sure that the recaptcha-solver.crx binary file is present in the src/extensions folder. Either download it with `git lfs` or download it as a raw file from the [github repo](https://github.com/speedyconzales/series-scraper/blob/main/src/extensions/recaptcha-solver.crx)

## Usage
1. use `main.py`
    - `python main.py <url>` to run the scraper
    - `python main.py --help` for more information
3. provide the url of the series. The `series-name` has to be present in the url.  
  That means: navigate to one of the supported sites. Search for the series you want to download and simply copy/paste the url. The url should look like  
  `https://aniworld.to/anime/stream/<series-name>` or  
  `https://s.to/serie/stream/<series-name>` or  
  `https://bs.to/serie/<series-name>`
4. use optional argument `-l` to choose the language of the content being either `Ger-Sub`, `Eng-Sub` or `English`. Default is `Deutsch`
5. use optional argument `-s` for the season number. If not specified all seasons will be scraped but not the movies or specials. -> Providing `0` as season number scrapes the respective movies or specials of that series
6. use optional argument `-e` for the episode number. If not specified all episodes of the season will be scraped
7. use optional argument `-t` to specify the number of threads or concurrent downloads. Default is 2. Do not choose too high numbers as the server might block too frequent requests
8. use optional argument `-a` to declare this content as anime. Only useful for `bs.to` as it does not distinguish between series and anime on the site

## Credits
- [wolfswolke](https://github.com/wolfswolke) for the continuous implementation of [aniworld_scraper](https://github.com/wolfswolke/aniworld_scraper)
