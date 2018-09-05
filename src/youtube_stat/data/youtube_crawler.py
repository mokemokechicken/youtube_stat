import json
from copy import copy
from logging import getLogger
from os.path import exists
from typing import List

from youtube_stat.config import Config
from youtube_stat.lib.file_util import save_json_to_file, load_json_from_file
from youtube_stat.lib.http_lib import http_get

logger = getLogger()


class YoutubeCrawler:
    def __init__(self, config: Config):
        self.config = config

    def start(self):
        assert self.config.data.channel_id, "channel_id is not specified"
        assert self.config.resource.youtube_api_key, "API Key is not specified"

        video_list = self.fetch_video_list()
        self.fetch_video_detail(video_list)

    def fetch_video_list(self):
        video_list_path = f'{self.config.resource.crawler_data_dir}/{self.config.resource.video_list_name}'
        if not exists(video_list_path):
            video_list = self.call_fetch_video_list()
            save_json_to_file(video_list_path, video_list)
        else:
            logger.info("loading video list from cache")
            video_list = load_json_from_file(video_list_path)
        return video_list

    def call_fetch_video_list(self):
        url = 'https://www.googleapis.com/youtube/v3/search'
        base_params = dict(
            part="snippet,id",
            channelId=self.config.data.channel_id,
            order="date",
            key=self.config.resource.youtube_api_key,
            maxResults=50,
        )
        page_token = None
        video_list = []
        while True:
            params = copy(base_params)
            if page_token:
                params['pageToken'] = page_token
            ret = json.loads(http_get(url, params))
            page_token = ret.get('nextPageToken')
            if ret.get("items"):
                video_list += ret.get("items")
            else:
                break
            if not page_token:
                break
        return video_list

    def fetch_video_detail(self, video_list):
        fetch_video_detail_list = []
        detail_path = f'{self.config.resource.crawler_data_dir}/{self.config.resource.video_detail_list_name}'

        if exists(detail_path):
            with open(detail_path, "rt") as f:
                video_detail_list = json.load(f)
        else:
            video_detail_list = []
        existing_video_set = set([x.get("id") for x in video_detail_list])

        for video_info in video_list:
            video_id = video_info['id'].get('videoId')
            if video_id and video_id not in existing_video_set:
                fetch_video_detail_list.append(video_id)

        if fetch_video_detail_list:
            video_detail_list += self.call_fetch_video_detail(fetch_video_detail_list)
            save_json_to_file(detail_path, video_detail_list)
        else:
            logger.info("skip fetch video details")
        return video_detail_list

    def call_fetch_video_detail(self, video_list: List[str]):
        video_detail_list = []
        url = 'https://www.googleapis.com/youtube/v3/videos'

        for i in range(0, len(video_list), 50):
            params = dict(
                part='snippet,statistics',
                id=",".join(video_list[i:min(len(video_list), i+50)]),
                key=self.config.resource.youtube_api_key,
            )
            response = json.loads(http_get(url, params))
            video_detail_list += response['items']
        return video_detail_list

