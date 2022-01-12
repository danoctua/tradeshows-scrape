import datetime

from exhibitions.spiders.base_spiders.base_expocad_spider import BaseExpocadSpider


class BarAndRestaurantSpider(BaseExpocadSpider):
    name = "BarAndRestaurantSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 21)
    EXHIBITION_NAME = "Nightclub & Bar Show"
    EXHIBITION_WEBSITE = "https://www.barandrestaurantexpo.com/"

    URLS = [
        "https://www.expocad.com/host/fx/questex/22bre/22bre.xml",
    ]
