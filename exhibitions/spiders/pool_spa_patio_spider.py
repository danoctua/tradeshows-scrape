import datetime
from exhibitions.spiders.base_spiders.base_map_your_show_spider import (
    BaseMapYourShowSpider,
)


class PoolSpaPatioSpider(BaseMapYourShowSpider):
    name = "PoolSpaPatioSpider"

    EXHIBITION_DATE = datetime.date(2021, 11, 16)
    EXHIBITION_NAME = "Pool, Spa, Patio Expo"
    EXHIBITION_WEBSITE = "https://www.poolspapatio.com/en/home.html"

    EXHIBITION_CODE = "psp211"
