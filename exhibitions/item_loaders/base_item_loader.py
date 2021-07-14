from itemloaders.processors import TakeFirst
from scrapy.loader import ItemLoader
from typing import List, Optional


def join_loaded(list_of_attributes: List[str], separator: str = " | "):
    return separator.join(
        attribute.strip() for attribute in list_of_attributes if attribute
    ) if list_of_attributes else None


class BaseItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    @staticmethod
    def address_in(address_lines: List[Optional[str]]):
        return join_loaded(address_lines, ", ")

    @staticmethod
    def category_in(categories: List[Optional[str]]):
        return join_loaded(categories, " | ")
