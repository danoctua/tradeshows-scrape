from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from typing import List


class FurnitureManufacturerItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    @staticmethod
    def category_in(category_list: List[str]) -> str:
        # remove empty strings
        return " | ".join([c.strip() for c in category_list if c.strip()])

    @staticmethod
    def address_in(address_lines: List[str]) -> str:
        # remove empty strings
        return ", ".join([a.strip() for a in address_lines if a.strip()])
