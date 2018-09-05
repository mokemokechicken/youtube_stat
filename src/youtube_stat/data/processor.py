import re
from collections import namedtuple, Counter
from logging import getLogger
from typing import List

from youtube_stat.config import Config
from youtube_stat.lib.datetime_util import parse_date_str
from youtube_stat.lib.file_util import load_json_from_file, save_json_to_file
from youtube_stat.lib.japanese_parser import JapaneseParserByYahooAPI
import pandas as pd

logger = getLogger(__name__)

DataRecord = namedtuple('DataRecord', 'id date wday title view like dislike comment words')
DELI = "\t"
WORD_DELI = "|"


class DataProcessor:
    USE_POS_SET = {'名詞', '動詞', '形容動詞', '形容詞', '副詞'}

    def __init__(self, config: Config):
        self.config = config

    def parse_text(self):
        logger.info("start parse text")
        detail_path = f"{self.config.resource.crawler_data_dir}/{self.config.resource.video_detail_list_name}"
        video_detail_list = load_json_from_file(detail_path)
        parser = JapaneseParserByYahooAPI(self.config)
        kp = self.config.data.key_parsed_title
        updated = False

        for video_info in video_detail_list:
            title = video_info.get("snippet", {}).get("title")
            if title and not video_info.get(kp):
                result = parser.parse_japanese(title)
                video_info[kp] = result
                updated = True

        if updated:
            save_json_to_file(detail_path, video_detail_list)
        else:
            logger.info("skip parse text")

    def create_dataset(self):
        logger.info("start create_dataset")
        detail_path = f"{self.config.resource.crawler_data_dir}/{self.config.resource.video_detail_list_name}"
        video_detail_list = load_json_from_file(detail_path)

        data = []
        word_set = self.pickup_words(video_detail_list)
        ignore_title_list = [re.compile(x) for x in self.config.data.ignore_title_list]

        for vi in video_detail_list:
            sp = vi.get("snippet")
            stat = vi.get("statistics")
            if not sp or not stat:
                continue
            if not all([reg.search(sp['title']) is None for reg in ignore_title_list]):
                continue

            dt = parse_date_str(sp['publishedAt'])
            words = vi[self.config.data.key_parsed_title]

            use_words = set()
            for w in words:
                if w['surface'] in word_set:
                    use_words.add(w['surface'])

            if all([re.search("^[a-zA-Z0-9'’]+$", x) for x in use_words]):
                continue

            record = DataRecord(
                id=vi['id'],
                date=dt.strftime("%Y/%m/%d"),
                wday=dt.weekday(),
                title=sp['title'],
                view=stat['viewCount'],
                like=stat.get('likeCount', 0),
                dislike=stat.get('dislikeCount', 0),
                comment=stat['commentCount'],
                words=WORD_DELI.join(use_words),
            )
            if record.words:
                data.append(record)

        with open(self.dataset_path, "wt") as f:
            f.write(DELI.join(DataRecord._fields)+"\n")
            for rec in data:
                f.write(DELI.join([str(x) for x in rec]) + "\n")

    def pickup_words(self, video_detail_list):
        ignore_word_list = [re.compile(x) for x in self.config.data.ignore_word_list]
        word_set = set()
        for vi in video_detail_list:
            words = vi[self.config.data.key_parsed_title]
            for word in words:
                if word['pos'] in self.USE_POS_SET:
                    text = word['surface']
                    if all([reg.search(text) is None for reg in ignore_word_list]):
                        word_set.add(text)
        return word_set

    def convert_to_training_data(self):
        with open(self.dataset_path, "rt") as f:
            f.readline()  # skip headers
            data = [DataRecord(*l.strip().split(DELI)) for l in f]

        word_index_dict, month_index_dict, wday_index_dict = self.collect_one_hot_info(data)

        train_data = []
        before_date = self.config.data.before_date and parse_date_str(self.config.data.before_date)
        for rec in data:
            date = parse_date_str(rec.date)
            if before_date and before_date < date:
                continue

            row = [rec.id]
            row += [rec.view, rec.like, rec.dislike, rec.comment]
            row += self.to_one_hot(month_index_dict, (date.year, date.month))
            row += self.to_one_hot(wday_index_dict, date.weekday())

            words = [w for w in rec.words.split(WORD_DELI) if w in word_index_dict]
            row += self.to_one_hot(word_index_dict, words)
            train_data.append(row)

        columns = ["id"]
        columns += ["view", "like", "dislike", "comment"]
        columns += ["%d-%02d" % x for x in sorted(month_index_dict.keys())]
        columns += "Mon Tue Wed Thr Fri Sat Sun".split(" ")
        columns += ["w%03d" % i for i in range(len(word_index_dict))]

        with open(self.training_data_path, "wt") as f:
            f.write(",".join(columns) + "\n")
            for d in train_data:
                f.write(",".join([str(x) for x in d])+"\n")

        save_json_to_file(self.word_index_path, word_index_dict)

    def load_training_data(self):
        return pd.read_csv(self.training_data_path)

    def load_basic_data(self):
        return pd.read_csv(self.dataset_path, sep=DELI, quoting=3)

    def collect_one_hot_info(self, data: List[DataRecord]):
        word_counter = Counter()
        month_set = set()
        before_date = self.config.data.before_date and parse_date_str(self.config.data.before_date)

        for rec in data:
            word_counter.update(rec.words.split(WORD_DELI))
            date = parse_date_str(rec.date)
            if date <= before_date:
                month_set.add((date.year, date.month))

        word_list = list([w for w, c in word_counter.most_common() if c >= self.config.data.min_word_occur])
        month_list = list(sorted(month_set))
        word_index_dict = dict([w, i] for i, w in enumerate(word_list))
        month_index_dict = dict([w, i] for i, w in enumerate(month_list))
        wday_index_dict = dict([i, i] for i in range(7))
        return word_index_dict, month_index_dict, wday_index_dict

    @staticmethod
    def to_one_hot(index_dict, items):
        if not isinstance(items, list):
            items = [items]
        ret = [0] * len(index_dict)
        for item in items:
            ret[index_dict[item]] = 1
        return ret

    @property
    def dataset_path(self):
        return f"{self.config.resource.working_dir}/{self.config.resource.basic_dataset_name}"

    @property
    def training_data_path(self):
        return f"{self.config.resource.working_dir}/{self.config.resource.training_dataset_name}"

    @property
    def word_index_path(self):
        return f"{self.config.resource.working_dir}/{self.config.resource.word_index_name}"
