import datetime

from exhibitions.spiders.base_spiders.base_se_spider import BaseSESpider


class StockholmFurnitureSpider(BaseSESpider):
    name = "StockholmFurnitureSpider"

    EXHIBITION_DATE = datetime.date(2022, 2, 8)
    EXHIBITION_NAME = "Stockholm Furniture & Lighting Fair"
    EXHIBITION_WEBSITE = "https://www.stockholmfurniturelightfair.se/"

    SHOW_SLUG = "stockholmfurniturelightfair"
    FROM_NODE = "5E8F501D019E4094B0E7A1617344EDB5"
