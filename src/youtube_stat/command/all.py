from logging import getLogger

from youtube_stat.command import crawl, pre, analysis
from youtube_stat.config import Config

logger = getLogger(__name__)


def start(config: Config):
    crawl.start(config)
    pre.start(config)
    analysis.start(config)
