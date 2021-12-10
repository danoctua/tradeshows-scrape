import datetime

from exhibitions.spiders.base_spiders.base_se_spider import BaseSESpider


class FormexSpider(BaseSESpider):
    name = "FormexSpider"

    EXHIBITION_DATE = datetime.date(2022, 1, 18)
    EXHIBITION_NAME = "FORMEX"
    EXHIBITION_WEBSITE = "https://www.formex.se/"

    SHOW_SLUG = "formex"
    FROM_NODE = "E36AD80B8B1B4FBD8D175087F8828B06"
