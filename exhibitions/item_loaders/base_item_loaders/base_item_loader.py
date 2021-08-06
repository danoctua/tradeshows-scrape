from itemloaders.processors import MapCompose, TakeFirst
from scrapy.loader import ItemLoader
from typing import List, Optional


def join_loaded(list_of_attributes: List[str], separator: str = " | "):
    return separator.join(
        attribute.strip() for attribute in list_of_attributes if attribute
    ) if list_of_attributes else None


class BaseItemLoader(ItemLoader):
    default_output_processor = TakeFirst()

    exhibitor_name_in = MapCompose(str.strip)
    description_in = MapCompose(str.strip)

    @staticmethod
    def address_out(address_lines: List[Optional[str]]):
        return join_loaded(address_lines, " ")

    @staticmethod
    def category_out(categories: List[Optional[str]]):
        return join_loaded(categories, " | ")
