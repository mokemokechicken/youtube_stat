from logging import getLogger

from youtube_stat.config import Config
from youtube_stat.data.youtube_crawler import YoutubeCrawler

logger = getLogger(__name__)


def start(config: Config):
    logger.info(f"start crawl")
    CrawlCommand(config).start()


class CrawlCommand:
    def __init__(self, config: Config):
        self.config = config

    def start(self):
        logger.info(f"channel_id={self.config.data.channel_id}")
        crawler = YoutubeCrawler(self.config)
        crawler.start()

