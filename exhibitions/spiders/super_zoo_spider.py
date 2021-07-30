import datetime

from exhibitions.spiders.base_spiders.base_a2z_spider import BaseA2ZSpider


class SuperZooSpider(BaseA2ZSpider):
    name = "SuperZooSpider"

    EXHIBITION_DATE = datetime.date(2021, 8, 17)
    EXHIBITION_NAME = "SuperZoo"
    EXHIBITION_WEBSITE = "https://www.superzoo.org/"

    URLS = [
        "https://s23.a2zinc.net/clients/WPA/SZ2021/Public/Exhibitors.aspx",
    ]
