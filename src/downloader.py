import time
import requests
import threading
import subprocess
import platform
import os

from os import path
from .logger import Logger as logger

MODULE_LOGGER_HEAD = "downloader.py -> "


def already_downloaded(file_name):
    if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
        logger.info(MODULE_LOGGER_HEAD + "Episode {} already downloaded.".format(file_name))
        return True
    logger.debug(MODULE_LOGGER_HEAD + "File not downloaded. Downloading: {}".format(file_name))
    return False


def download_episode(url, file_name):
    try:
        ffmpeg_cmd = ['ffmpeg', '-i', url, '-c', 'copy', file_name]
        logger.info(MODULE_LOGGER_HEAD + "File {} added to queue.".format(file_name))
        if platform.system() == "Windows":
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.success(MODULE_LOGGER_HEAD + "Finished download of {}.".format(file_name))
    except subprocess.CalledProcessError as e:
        os.remove(file_name) if os.path.exists(file_name) else None
        logger.error(MODULE_LOGGER_HEAD + str(e))
        logger.error(MODULE_LOGGER_HEAD + "Could not download {}. Please manually download it later.".format(file_name))


def create_new_download_thread(thread_semaphore, active_threads, content_url, file_name):
     with thread_semaphore:
        thread = threading.Thread(target=download_episode,args=[content_url,file_name])
        active_threads.append(thread)
        thread.start()
