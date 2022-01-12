import datetime
from exhibitions.spiders.base_spiders.base_map_your_show_spider import (
    BaseMapYourShowSpider,
)


class GlobalPetExpoSpider(BaseMapYourShowSpider):
    name = "GlobalPetExpoSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 23)
    EXHIBITION_NAME = "Global Pet Expo"
    EXHIBITION_WEBSITE = "https://globalpetexpo.org/"

    EXHIBITION_CODE = "globalpetexpo22"
