import re
from typing import Optional

from itemloaders.processors import MapCompose, Join, TakeFirst

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
)


class FilterNone:
    def __init__(self, *args):
        self._none_values: tuple = args

    def __call__(self, value: Optional[list]) -> Optional[list]:
        return None if value in self._none_values else value


filter_none = FilterNone(False)
take_first = TakeFirst()

ENGLISH_ATTRIBUTE_REGEX = re.compile(r"\[en\](.*)<\/multi>")


class JDCItemLoader(BaseItemLoader):

    default_input_processor = MapCompose(filter_none, str, str.strip)

    @staticmethod
    def category_out(category_lines):
        print(category_lines)
        return Join(", ")(
            take_first(ENGLISH_ATTRIBUTE_REGEX.findall(category_line))
            for category_line in category_lines
            if category_line
        )
