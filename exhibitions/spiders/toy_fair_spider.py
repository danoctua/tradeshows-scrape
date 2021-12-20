import datetime
from exhibitions.spiders.base_spiders.base_map_your_show_spider import (
    BaseMapYourShowSpider,
)


class ToyFairSpider(BaseMapYourShowSpider):
    name = "ToyFairSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 9)
    EXHIBITION_NAME = "Toy Fair NY"
    EXHIBITION_WEBSITE = "https://toyfairny.com/"

    EXHIBITION_CODE = "tfny2022"
