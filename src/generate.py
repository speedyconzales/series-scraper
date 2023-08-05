import random
import string
import time


def make_play():
    token_length = 10
    characters = string.ascii_letters + string.digits

    # Generate a random token
    random_token = ''.join(random.choice(characters) for _ in range(token_length))
    expiry = int(time.time()) + 3600  # Set the expiry time (1 hour from now)

    return f"{random_token}?token=zoykt1y1skg9tlgvyjlh0ru2&expiry={expiry}"

# Example URL
base_url = "https://example.com/video.mp4"

# Call the make_play() function to generate the random token and add it to the URL
video_url_with_token = f"{base_url}/{make_play()}"

print("Original URL:", base_url)
print("URL with Random Token:", video_url_with_token)
