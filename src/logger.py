import logging

class Logger:
    SUCCESS = 25
    logging.addLevelName(SUCCESS, "SUCCESS")
    _logger = logging.getLogger("scraper_logger")
    _logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)

    @staticmethod
    def debug(message):
        Logger._logger.debug(message)
    
    @staticmethod
    def info(message):
        Logger._logger.info(message)

    @staticmethod
    def success(message, *args, **kwargs):
        if Logger._logger.isEnabledFor(Logger.SUCCESS):
            Logger._logger._log(Logger.SUCCESS, message, args, **kwargs)

    @staticmethod
    def warning(message):
        Logger._logger.warning(message)

    @staticmethod
    def error(message):
        Logger._logger.error(message)
