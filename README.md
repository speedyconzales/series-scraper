# Series-Scraper

## Supported Sites
headless and completely automated scraping of the following sites:
  - [aniworld.to](https://aniworld.to)
  - [s.to](https://s.to)
  - [bs.to](https://bs.to) -> uses headless browser for scraping and solving captchas

## Supported Hosters
- [VOE](https://voe.sx)
- [Vidoza](https://vidoza.net)
- [Doodstream](https://doodstream.com)
- [Streamtape](https://streamtape.com)

## Usage
* If you are familiar with docker 
   1. just use:
      ```bash
      docker pull speedyconzales/series-scraper 
      ```
   2. and then: 

      * either docker run
         ```bash 
         docker run \
         --rm \
         -e PUID=[YOUR_USER_ID] \
         -e PGID=[YOUR_GROUP_ID] \
         -v [PATH_TO_YOUR_ANIME_FOLDER]:/app/anime \
         -v [PATH_TO_YOUR_SERIES_FOLDER]:/app/series \
         speedyconzales/series-scraper \
         s6-setuidgid abc \
         python3 main.py
         ``` 
         followed by the [arguments](#arguments) you want to provide  

      * or docker compose  
         docker-compose.yml:
         ```yaml
         services:
         series-scraper:
            image: speedyconzales/series-scraper
            container_name: series-scraper
            volumes:
               - [PATH_TO_YOUR_ANIME_FOLDER]:/app/anime
               - [PATH_TO_YOUR_SERIES_FOLDER]:/app/series
            environment:
               - PUID=[YOUR_USER_ID]
               - PGID=[YOUR_GROUP_ID]
               - TZ=Europe/Berlin
         ```
         and run
         ```bash 
         docker compose run --rm s6-setuidgid abc python3 main.py
         ```
         followed by the [arguments](#arguments) you want to provide
* If you don't want to use docker or there is no suitable docker image available for your architecture, you can use the following steps to run the scraper:
   1. clone the repository

      ```bash
      git clone https://github.com/speedyconzales/series-scraper.git
      ```
   2. install the [dependencies](#dependencies)
   3. run the scraper 

      ```bash
      python3 main.py
      ``` 
      followed by the [arguments](#arguments) you want to provide

## Dependencies

1. install [ffmpeg](https://ffmpeg.org/download.html) and make sure it is in PATH -> `ffmpeg -version`
2. install [chrome](https://www.google.com/chrome/) or [chromium](https://www.chromium.org/getting-involved/download-chromium/)
3. install required python packages. Given: you have python3.12 installed 
   * either via `pipenv` and Pipfile 
      ```bash
      pipenv install
      pipenv shell
      ```
   * or create a virtual environment and install them via `pip` and requirements.txt
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      pip install -r requirements.txt
      ```
4. copy and rename `template.yml` to `config.yml` and fill in the required folder paths for the respective type of the content
5. if you want to download from [bs.to](?plain=1#L7) you need to make sure that the recaptcha-solver.crx binary file is present in the src/extensions folder. Either download it with `git lfs` or download it as a raw file from the [github repo](https://github.com/speedyconzales/series-scraper/blob/main/src/extensions/recaptcha-solver.crx)

## Arguments
|     Argument     | Function                                                                                                                                                                                                                                                                                                                                                                       |
| :--------------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|     `<url>`      | Provide the `<url>` of the series. The `series-name` has to be present in the url. That means: navigate to one of the supported sites. Search for the series you want to download and simply copy/paste the url. The url should look like `https://aniworld.to/anime/stream/<series-name>` or `https://s.to/serie/stream/<series-name>` or `https://bs.to/serie/<series-name>` |
|     `--help`     | get a list of all available arguments                                                                                                                                                                                                                                                                                                                                          |
| `-l, --language` | **Default:** `Deutsch`. Choose the language of the content being either `Ger-Sub`, `Eng-Sub` or `English`                                                                                                                                                                                                                                                                      |
|  `-s, --season`  | **Default:** All seasons will be scraped but not the movies or specials. Choose the season number. -> Providing `0` as season number scrapes the respective movies or specials of that series                                                                                                                                                                                  |
| `-e, --episode`  | **Default:** All episodes of the season will be scraped. Choose either one episode or a list of episodes separated by spaces. You can also specify a range of episodes e.g.: `-e 2 3 10-15 17`                                                                                                                                                                                 |
| `-t, --threads`  | **Default:** 2. Specify the number of threads or concurrent downloads. Do not choose too high numbers as the server might block too frequent requests                                                                                                                                                                                                                          |
| `-p, --provider` | **Default:** Downloads will follow this priority: Vidoza > VOE > Doodstream > Streamtape. If the episode is not available on the hoster it will try the next. Specify the hoster/provider you want to download from                                                                                                                                                            |
|  `-a, --anime`   | Declare this content as anime. Only useful for `bs.to` as it does not distinguish between series and anime on the site                                                                                                                                                                                                                                                         |

## Credits
- [wolfswolke](https://github.com/wolfswolke) for the continuous implementation of [aniworld_scraper](https://github.com/wolfswolke/aniworld_scraper)
