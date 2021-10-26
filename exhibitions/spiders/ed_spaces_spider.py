import datetime

from exhibitions.spiders.base_spiders.base_a2z_spider import BaseA2ZSpider


class EdSpacesSpider(BaseA2ZSpider):
    name = "EdSpacesSpider"

    EXHIBITION_DATE = datetime.date(2021, 11, 3)
    EXHIBITION_NAME = "ED Spaces"
    EXHIBITION_WEBSITE = "https://ed-spaces.com/"

    URLS = [
        "https://edspaces.a2zinc.net/Edspaces2021/Public/eventmap.aspx?shMode=E",
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "Upgrade-Insecure-Requests": 1,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host": "edspaces.a2zinc.net",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-GPC": 1,
    }
