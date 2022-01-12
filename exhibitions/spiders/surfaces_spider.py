import datetime

from exhibitions.spiders.base_spiders.base_map_your_show_spider import (
    BaseMapYourShowSpider,
)


class SurfacesSpider(BaseMapYourShowSpider):
    name = "SurfacesSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 1)
    EXHIBITION_NAME = "Surfaces"
    EXHIBITION_WEBSITE = "https://www.intlsurfaceevent.com/"

    EXHIBITION_CODE = "sur221"
