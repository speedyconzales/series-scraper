# Series-Scraper

## Supported Sites
- headless and completely automated scraping of the following sites:
  - [aniworld.to](https://aniworld.to)
  - [s.to](https://s.to)
- needs a GUI and requires user interaction (solve captchas):
  - [bs.to](https://bs.to)

## Supported Hosters
- [VOE](https://voe.sx)
- [Vidoza](https://vidoza.net)
- [Streamtape](https://streamtape.com)

## Dependencies

1. install [ffmpeg](https://ffmpeg.org/download.html) and make sure it is in PATH -> `ffmpeg -version`
2. install [chrome](https://www.google.com/chrome/) or [chromium](https://www.chromium.org/getting-involved/download-chromium/)
3. install requirements via pipenv and Pipfile OR create a virtual environment and install them via pip and requirements.txt
4. copy and rename template.yml to config.yml and fill in the required folder paths for the respective type of the content

## Usage
1. use `main.py`
    - `python main.py <type[anime,serie]> <url> <language[Deutsch,Ger-Sub,Eng-Sub,English]>` to run the scraper
    - `python main.py --help` for more information
2. choose either `anime` or `serie` for the corresponding type and output path
3. provide the url of the series. The `series-name` has to be present in the url.  
That means: navigate to one of the supported sites. Search for the series you want to download and simply copy/paste the url. The url should look like  
`https://aniworld.to/anime/stream/<series-name>` or  
`https://s.to/serie/stream/<series-name>` or  
`https://bs.to/serie/<series-name>`
4. choose the language of the content being either `Deutsch`, `Ger-Sub`, `Eng-Sub` or `English`
5. use optional argument `-s` for the season number. If not specified all seasons will be scraped but not the movies or specials. -> Providing `0` as season number scrapes the respective movies or specials of that series
6. use optional argument `-e` for the episode number. If not specified all episodes of the season will be scraped
7. use optional argument `-t` to specify the number of threads or concurrent downloads. Default is 2. Do not choose too high numbers as the server might block too frequent requests

## Credits
- [wolfswolke](https://github.com/wolfswolke) for the continuous implementation of [aniworld_scraper](https://github.com/wolfswolke/aniworld_scraper)
