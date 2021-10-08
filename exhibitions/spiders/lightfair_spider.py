import datetime
from exhibitions.spiders.base_spiders.base_map_your_show_spider import BaseMapYourShowSpider


class LightFairSpider(BaseMapYourShowSpider):
    name = "LightFairSpider"

    EXHIBITION_DATE = datetime.date(2021, 10, 25)
    EXHIBITION_NAME = "Lightfair"
    EXHIBITION_WEBSITE = "https://www.lightfair.com/"

    EXHIBITION_CODE = "lf2021"
