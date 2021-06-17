from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from typing import List, Optional


class CoveringsItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    @staticmethod
    def address_in(address_lines: List[Optional[str]]):
        return ", ".join(a.strip() for a in address_lines if a)

    @staticmethod
    def category_in(categories: List[Optional[str]]):
        return ", ".join(c.strip() for c in categories if c)
