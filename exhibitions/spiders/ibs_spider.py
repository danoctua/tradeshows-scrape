import datetime

from exhibitions.spiders.base_spiders.base_a2z_spider import BaseA2ZSpider


class IBSSpider(BaseA2ZSpider):
    name = "IBSSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 8)
    EXHIBITION_NAME = "IBS 2022"
    EXHIBITION_WEBSITE = "https://www.buildersshow.com/"

    URLS = [
        "https://s23.a2zinc.net/clients/nahb/ibs22/Public/exhibitors.aspx?Index=All",
    ]

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "Upgrade-Insecure-Requests": 1,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Host": "s23.a2zinc.net",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Sec-GPC": 1,
    }