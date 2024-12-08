import os
import subprocess

from src.logger import logger, SUCCESS


def already_downloaded(file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        logger.info(f"Episode '{file_name}' already downloaded.")
        return True
    logger.debug(f"Episode not downloaded. Downloading: {file_name}")
    return False


def download_episode(url, file_name, episode, provider):
    try:
        ffmpeg_cmd = ["ffmpeg", "-i", url, "-c", "copy", "-nostdin", file_name]
        if provider == "Doodstream":
            ffmpeg_cmd.insert(1, "Referer: https://d0000d.com/")
            ffmpeg_cmd.insert(1, "-headers")
        elif provider == "Vidmoly":
            ffmpeg_cmd.insert(1, "Referer: https://vidmoly.to/")
            ffmpeg_cmd.insert(1, "-headers")
        logger.info(f"Episode '{file_name}' added to queue.")
        subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        logger.log(SUCCESS, f"Finished download of {file_name}.")
        return None
    except subprocess.CalledProcessError as e:
        os.remove(file_name) if os.path.exists(file_name) else None
        logger.error(str(e))
        logger.error(f"Could not download {file_name}.")
        return episode


def create_new_download_thread(executor, content_url, file_name, episode, provider):
    return executor.submit(download_episode, content_url, file_name, episode, provider)
