import datetime
from exhibitions.spiders.base_spiders.base_messe_frankfurt_spider import (
    BaseMesseFrankfurtSpider,
)


class HeimTextilSpider(BaseMesseFrankfurtSpider):
    name = "HeimTextilSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 13)
    EXHIBITION_NAME = "heimtextil"
    EXHIBITION_WEBSITE = "https://heimtextil.messefrankfurt.com"

    FIND_EVENT_VARIABLE: str = "HEIMTEXTIL"
    EXHIBITOR_SEARCH_URL: str = (
        "https://exhibitorsearch.messefrankfurt.com/service/esb/2.1/search/exhibitor"
    )
