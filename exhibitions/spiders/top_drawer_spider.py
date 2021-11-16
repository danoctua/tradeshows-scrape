import datetime

from exhibitions.spiders.base_spiders.base_asp_spider import BaseASPSpider


class TopDrawerSpider(BaseASPSpider):
    name = "TopDrawerSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 16)
    EXHIBITION_NAME = "Top Drawer Spring"
    EXHIBITION_WEBSITE = "https://www.topdrawer.co.uk/"


    URLS = [
        "https://www.topdrawer.co.uk/s-s-2-2-edition-exhibiting-brands?&categories=1F33EDE6-5056-B733-490CE9290DAF9BF0&searchgroup=00000001-s-s-2-2-edition-exhibiting-brands",
    ]
