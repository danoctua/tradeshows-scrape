import datetime
import re

from scrapy.http import Response

from exhibitions.spiders.base_spiders.base_asp_spider import BaseASPSpider


EXHIBITOR_URL_REGEX = re.compile(r"openRemoteModal\('(?P<url>[^']*)'")


class HomeBuildingRenovationSpider(BaseASPSpider):
    name = "HomeBuildingRenovationSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 15)
    EXHIBITION_NAME = "Homebuilding & Renovation Show"
    EXHIBITION_WEBSITE = "https://farnborough.homebuildingshow.co.uk/"

    URLS = [
        "https://farnborough.homebuildingshow.co.uk/exhibitor-list",
    ]

    def fetch_exhibitors(self, response: Response):
        exhibitors = response.xpath(
            "//a[@class='m-exhibitors-list__items__item__header__title__link js-librarylink-entry']/@href"
        ).getall()
        for exhibitor in exhibitors:
            exhibitor_url_search = EXHIBITOR_URL_REGEX.search(exhibitor)
            if exhibitor_url_search:
                yield response.follow(
                    url=exhibitor_url_search.group("url"),
                    callback=self.parse_exhibitors,
                    headers=self.HEADERS,
                )
