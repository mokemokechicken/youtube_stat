import os
from pathlib import Path

from moke_config import ConfigBase


def _system_dir():
    return Path(__file__).parent.parent.parent


class Config(ConfigBase):
    def __init__(self):
        self.runtime = RuntimeConfig()
        self.resource = ResourceConfig(self)
        self.data = DataConfig()
        self.model = ModelConfig()
        self.training = TrainingConfig()


class RuntimeConfig(ConfigBase):
    def __init__(self):
        self.args = None


class ResourceConfig(ConfigBase):
    def __init__(self, config: Config):
        self._config = config
        self.system_dir = _system_dir()

        # Log
        self.log_dir = self.system_dir / "log"
        self.tensorboard_dir = self.log_dir / "tensorboard"
        self.main_log_path = self.log_dir / "main.log"
        self.resource_dir = self.system_dir / "resource"

        # crawler
        self.crawler_dir_name = 'crawler'
        self.youtube_api_key = os.environ.get('YOUTUBE_API_KEY')
        self.video_list_name = 'video_list.json'
        self.video_detail_list_name = 'video_detail_list.json'

        # preprocess text
        self.yahoo_api_client_id = os.environ.get('YAHOO_API_CLIENT_ID')

        # dataset
        self.basic_dataset_name = 'dataset.tsv'
        self.training_dataset_name = 'train.csv'
        self.word_index_name = "words.json"

        # analyze
        self.summary_dist_graph_name = 'summary_dist.png'
        self.target_dist_graph_name = 'target_dist.png'
        self.summary_template_name = 'summary.html'

    @property
    def working_dir(self):
        return f"{self.system_dir}/working/{self._config.data.channel_id}"

    @property
    def crawler_data_dir(self):
        return f"{self.working_dir}/{self.crawler_dir_name}"

    def create_base_dirs(self):
        dirs = [self.log_dir, self.working_dir, self.crawler_data_dir]

        for d in dirs:
            os.makedirs(d, exist_ok=True)


class DataConfig(ConfigBase):
    def __init__(self):
        self.channel_id = None
        self.key_parsed_title = 'parsed_title'
        self.ignore_title_list = [
            # r"""^([-!0-9a-zA-Z|"'’:?.,\[\]【】]|\s)+$""",
        ]
        self.ignore_word_list = [
            r"""^[0-9]+$""",
        ]
        self.min_word_occur = 5
        self.before_date = None


class ModelConfig(ConfigBase):
    def __init__(self):
        self.n_bins = 256
        self.n_levels = 2  # 4
        self.n_depth = 1   # 32
        self.hidden_channel_size = 16  # 512


class TrainingConfig(ConfigBase):
    def __init__(self):
        self.batch_size = 1
        self.lr = 0.0001
        self.lr_min = 0.000001
        self.lr_patience = 5
        self.lr_decay = 0.1
        self.epochs = 10
        self.steps_per_epoch = 1  # None means auto calculated
        self.sample_every_n_epoch = 5
        self.sample_n_image = 10
