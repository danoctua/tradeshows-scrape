import datetime
from exhibitions.spiders.base_spiders.base_messe_frankfurt_spider import (
    BaseMesseFrankfurtSpider,
)


class AmbienteSpider(BaseMesseFrankfurtSpider):
    name = "AmbienteSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 11)
    EXHIBITION_NAME = "Ambiente"
    EXHIBITION_WEBSITE = "https://ambiente.messefrankfurt.com"

    FIND_EVENT_VARIABLE: str = "AMBIENTE"
    EXHIBITOR_SEARCH_URL: str = (
        "https://exhibitorsearch.messefrankfurt.com/service/esb/2.1/search/exhibitor"
    )
