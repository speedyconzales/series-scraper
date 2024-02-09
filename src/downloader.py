import os
import platform
import subprocess

from src.logger import Logger as logger

MODULE_LOGGER_HEAD = "downloader.py -> "


class ProviderError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def already_downloaded(file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        logger.info(MODULE_LOGGER_HEAD + f"Episode '{file_name}' already downloaded.")
        return True
    logger.debug(
        MODULE_LOGGER_HEAD + f"Episode not downloaded. Downloading: {file_name}"
    )
    return False


def download_episode(url, file_name, episode):
    try:
        ffmpeg_cmd = ["ffmpeg", "-i", url, "-preset", "veryslow", "-crf", "18", "-nostdin", file_name]
        logger.info(MODULE_LOGGER_HEAD + f"Episode '{file_name}' added to queue.")
        if platform.system() == "Windows":
            subprocess.run(
                ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        else:
            subprocess.run(
                ffmpeg_cmd,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        logger.success(MODULE_LOGGER_HEAD + f"Finished download of {file_name}.")
        return None
    except subprocess.CalledProcessError as e:
        os.remove(file_name) if os.path.exists(file_name) else None
        logger.error(MODULE_LOGGER_HEAD + str(e))
        logger.error(
            MODULE_LOGGER_HEAD
            + f"Could not download {file_name}. Please manually download it later."
        )
        return episode


def create_new_download_thread(executor, content_url, file_name, episode):
    return executor.submit(download_episode, content_url, file_name, episode)
