import re
from typing import List, Optional
from w3lib.html import remove_tags

from itemloaders.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader


def join_loaded(list_of_attributes: List[str], separator: str = " | "):
    return (
        separator.join(
            attribute.strip() for attribute in list_of_attributes if attribute
        )
        if list_of_attributes
        else None
    )


class BaseItemLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()

    description_in = MapCompose(str.strip, remove_tags)
    manufacturers_out = Join(" | ")
    brands_out = Join(" | ")
    category_out = Join(" | ")
    address_out = Join(", ")

    @staticmethod
    def address_in(address_lines: List[Optional[str]]):
        return [a.strip() for a in address_lines if isinstance(a, str) and a.strip()]
