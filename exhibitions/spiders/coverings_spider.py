import datetime

from exhibitions.spiders.base_spiders.base_a2z_spider import BaseA2ZSpider


class CoveringsSpider(BaseA2ZSpider):
    name = "CoveringsSpider"

    EXHIBITION_DATE = datetime.date(2021, 7, 7)
    EXHIBITION_NAME = "Coverings"
    EXHIBITION_WEBSITE = "https://www.coverings.com/"

    URLS = [
        "https://expo.coverings.com/Cov2021/Public/exhibitors.aspx?Index=All",
    ]
