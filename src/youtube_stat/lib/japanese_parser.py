from xml.etree import ElementTree

from youtube_stat.config import Config
from youtube_stat.lib.http_lib import http_get


class JapaneseParserByYahooAPI:  # limit: 50000 req/day
    def __init__(self, config: Config):
        self.config = config

    def parse_japanese(self, text: str, use_types=None):
        assert self.config.resource.yahoo_api_client_id, "Please specify Yahoo API Client ID"
        url = 'https://jlp.yahooapis.jp/MAService/V1/parse'
        params = dict(
            appid=self.config.resource.yahoo_api_client_id,
            sentence=str(text),
            results='ma,uniq',
            uniq_by_baseform='true',
        )
        ret = http_get(url, params)
        root = ElementTree.fromstring(ret.decode())
        namespaces = {"a": 'urn:yahoo:jp:jlp'}
        # ma_result = root.find("./a:ma_result", namespaces=namespaces)
        uniq_result = root.find("./a:uniq_result", namespaces=namespaces)
        word_list = uniq_result.findall(".//a:word", namespaces=namespaces)

        tags = ['count', 'surface', 'pos']
        uniq_list = []
        for we in word_list:
            d = dict([(x, we.findtext(f"a:{x}", namespaces=namespaces)) for x in tags])
            if use_types and d['pos'] not in use_types:
                continue
            uniq_list.append(d)
        return uniq_list
