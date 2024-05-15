import os
import platform
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
        ffmpeg_cmd = ["ffmpeg", "-headers", "Referer: https://d0000d.com/", "-i", url, "-c", "copy", "-nostdin", file_name] if provider == "Doodstream" \
        else ["ffmpeg", "-i", url, "-c", "copy", "-nostdin", file_name]
        logger.info(f"Episode '{file_name}' added to queue.")
        if platform.system() == "Windows":
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.run(
                ffmpeg_cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        logger.log(SUCCESS, f"Finished download of {file_name}.")
        return None
    except subprocess.CalledProcessError as e:
        os.remove(file_name) if os.path.exists(file_name) else None
        logger.error(str(e))
        logger.error(f"Could not download {file_name}.")
        return episode


def create_new_download_thread(executor, content_url, file_name, episode, provider):
    return executor.submit(download_episode, content_url, file_name, episode, provider)
