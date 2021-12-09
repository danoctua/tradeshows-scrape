import datetime

from exhibitions.spiders.base_spiders.base_asp_spider import BaseASPSpider


class SpringFairSpider(BaseASPSpider):
    name = "SpringFairSpider"

    EXHIBITION_DATE = datetime.date(2022, 6, 2)
    EXHIBITION_NAME = "Spring Fair"
    EXHIBITION_WEBSITE = "https://www.springfair.com/welcome"

    URLS = [
        "https://www.springfair.com/exhibitors",
    ]
