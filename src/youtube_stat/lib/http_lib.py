from logging import getLogger
from time import sleep
from urllib import request, parse
from urllib.error import HTTPError

logger = getLogger()


def http_get(url, params=None, max_retry=5):
    req_url = '{}?{}'.format(url, parse.urlencode(params))
    logger.debug(f"GET {req_url}")
    body = None
    last_error = None
    for i in range(max_retry):
        try:
            req = request.Request(req_url)
            with request.urlopen(req) as res:
                body = res.read()
        except HTTPError as e:
            last_error = e
            if e.code < 500:
                break
            sleep(i * 2)

    if body is None:
        raise last_error
    return body
