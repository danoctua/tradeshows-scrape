import datetime
from exhibitions.spiders.base_spiders.base_messe_frankfurt_spider import (
    BaseMesseFrankfurtSpider,
)


class ChristmasWorldSpider(BaseMesseFrankfurtSpider):
    name = "ChristmasWorldSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 28)
    EXHIBITION_NAME = "Christmasworld 2022"
    EXHIBITION_WEBSITE = "https://christmasworld.messefrankfurt.com"

    FIND_EVENT_VARIABLE: str = "CHRISTMASWORLD"
    EXHIBITOR_SEARCH_URL: str = (
        "https://exhibitorsearch.messefrankfurt.com/service/esb/2.1/search/exhibitor"
    )
