import datetime
from exhibitions.spiders.base_spiders.base_messe_frankfurt_spider import (
    BaseMesseFrankfurtSpider,
)


class LightBuildingSpider(BaseMesseFrankfurtSpider):
    name = "LightBuildingSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 13)
    EXHIBITION_NAME = "Light+Building"
    EXHIBITION_WEBSITE = "https://light-building.messefrankfurt.com/frankfurt/en.html"

    FIND_EVENT_VARIABLE: str = "LIGHTBUILDING"
    EXHIBITOR_SEARCH_URL: str = (
        "https://exhibitorsearch.messefrankfurt.com/service/esb/2.1/search/exhibitor"
    )
