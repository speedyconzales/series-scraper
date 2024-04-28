import logging


class Logger:
    class ColoredFormatter(logging.Formatter):
        COLORS = {
            'DEBUG': '\033[94m',  # Blue
            'WARNING': '\033[93m',  # Yellow
            'ERROR': '\033[91m',   # Red
            'CRITICAL': '\033[95m',  # Magenta
            'SUCCESS': '\033[92m',   # Green for SUCCESS level
            'RESET': '\033[0m'   # Reset to default color
        }

        def format(self, record):
            log_level = record.levelname
            msg = super().format(record)
            color = self.COLORS.get(log_level, self.COLORS['RESET'])
            return f"{color}{msg}{self.COLORS['RESET']}"

    SUCCESS = 25
    logging.addLevelName(SUCCESS, "SUCCESS")
    _logger = logging.getLogger("scraper_logger")
    _logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter("%(levelname)s - %(asctime)s - %(message)s"))
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
            Logger._logger._log(Logger.SUCCESS,message, args, **kwargs)

    @staticmethod
    def warning(message):
        Logger._logger.warning(message)

    @staticmethod
    def error(message):
        Logger._logger.error(message)
