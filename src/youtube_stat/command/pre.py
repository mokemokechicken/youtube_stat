from logging import getLogger

from youtube_stat.config import Config
from youtube_stat.data.processor import DataProcessor

logger = getLogger(__name__)


def start(config: Config):
    logger.info(f"start preprocess")
    PreprocessCommand(config).start()


class PreprocessCommand:
    def __init__(self, config: Config):
        self.config = config

    def start(self):
        dp = DataProcessor(self.config)
        dp.parse_text()
        dp.create_dataset()
        dp.convert_to_training_data()
