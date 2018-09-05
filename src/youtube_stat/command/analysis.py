from logging import getLogger

from youtube_stat.analysis.analyze import Analyser
from youtube_stat.config import Config
from youtube_stat.data.processor import DataProcessor

logger = getLogger(__name__)


def start(config: Config):
    logger.info(f"start analysis")
    AnalysisCommand(config).start()


class AnalysisCommand:
    def __init__(self, config: Config):
        self.config = config

    def start(self):
        az = Analyser(self.config)
        az.start()
