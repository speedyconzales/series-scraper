import requests
import urllib
from bs4 import BeautifulSoup
from src.search_for_links import get_redirect_link
import re

STREAMTAPE_PATTERN = re.compile(r"get_video\?id=.+?&expires=.+?&ip=.+?&token=.+?\'")


def capture_video_stream(url, output_file):
    try:
        # Send a GET request to the URL to fetch the video stream
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"

        # Set the headers with the User-Agent
        headers = {"User-Agent": user_agent}

        response = requests.get(url, stream=True, headers=headers)
        print(response.text)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a file in binary write mode to save the video stream
            with open(output_file, "wb") as file:
                # Iterate over the content of the response and write it to the file
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
        else:
            print(f"Failed to fetch video stream. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")


def try_download(url, provider):
    html_page = urllib.request.urlopen(url)
    cache_link = STREAMTAPE_PATTERN.search(html_page.read().decode("utf-8"))
    if cache_link is None:
        return try_download(url, provider)
    cache_link = "https://" + provider + ".com/" + cache_link.group()[:-1]
    print(cache_link)
    capture_video_stream(cache_link, "this_is_it.mp4")


# Example usage
url = "https://chromotypic.com/e/t205ulfnkpc1"  # Replace with your video stream URL
output_file = "output_video.html"  # Replace with the desired output file name

capture_video_stream(url, output_file)
# try_download(redirect("https://aniworld.to", "https://aniworld.to/anime/stream/am-i-actually-the-strongest/staffel-1/episode-1", "Ger-Sub", "Streamtape"), "Streamtape")
