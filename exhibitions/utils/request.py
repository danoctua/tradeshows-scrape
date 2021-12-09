from urllib.parse import urlparse, parse_qsl, parse_qs, urlencode, urlunparse

from scrapy.http import Request

from typing import Dict, Optional, Union


URL_QUERY_INDEX = 4


class RequestWithParams(Request):
    def __init__(
        self, params: Optional[Dict[str, Union[str, int]]] = None, *args, **kwargs
    ):
        url = kwargs.get("url")
        if not url:
            raise AttributeError("Please, provide a proper URL")
        url_parts = list(urlparse(url))
        query = dict(parse_qs(url_parts[URL_QUERY_INDEX]))
        query.update(params)
        url_parts[URL_QUERY_INDEX] = urlencode(query, doseq=True)
        unparsed_url = urlunparse(url_parts)
        kwargs["url"] = unparsed_url
        super().__init__(*args, **kwargs)


def parse_params(url):
    url_parts = urlparse(url)
    return parse_qs(url_parts.query)
