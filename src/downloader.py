import threading
import subprocess
import platform
import os

from .logger import Logger as logger

MODULE_LOGGER_HEAD = "downloader.py -> "


class ProviderError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def already_downloaded(file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        logger.info(MODULE_LOGGER_HEAD + f"Episode '{file_name}' already downloaded.")
        return True
    logger.debug(MODULE_LOGGER_HEAD + f"Episode not downloaded. Downloading: {file_name}")
    return False


def download_episode(url, file_name):
    try:
        ffmpeg_cmd = ['ffmpeg', '-i', url, '-c', 'copy', file_name]
        logger.info(MODULE_LOGGER_HEAD + f"Episode '{file_name}' added to queue.")
        if platform.system() == "Windows":
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.success(MODULE_LOGGER_HEAD + f"Finished download of {file_name}.")
    except subprocess.CalledProcessError as e:
        os.remove(file_name) if os.path.exists(file_name) else None
        logger.error(MODULE_LOGGER_HEAD + str(e))
        logger.error(MODULE_LOGGER_HEAD + f"Could not download {file_name}. Please manually download it later.")
        raise ProviderError


def create_new_download_thread(thread_semaphore, active_threads, content_url, file_name):
     with thread_semaphore:
        thread = threading.Thread(target=download_episode,args=[content_url,file_name])
        active_threads.append(thread)
        thread.start()
