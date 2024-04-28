import logging


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',   # Red
        'CRITICAL': '\033[95m',  # Magenta
        'SUCCESS': '\033[92m',   # Green
        'RESET': '\033[0m'   # Reset to default color
    }

    def format(self, record):
        log_level = record.levelname
        msg = super().format(record)
        color = self.COLORS.get(log_level, self.COLORS['RESET'])
        return f"{color}{msg}{self.COLORS['RESET']}"

SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")
logger = logging.getLogger("series-scraper-logger")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter("%(levelname)s - %(asctime)s - %(filename)s -> %(message)s"))
logger.addHandler(console_handler)
