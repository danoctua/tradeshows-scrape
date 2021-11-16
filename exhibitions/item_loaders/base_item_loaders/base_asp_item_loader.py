import re
from itemloaders.processors import Join

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
)


BOOTH_NUMBER_REGEX = re.compile(r"Stand: (?P<booth_number>[^\r\n]*)")


class BaseASPItemLoader(BaseItemLoader):

    description_out = Join(" ")

    @staticmethod
    def country_out(address_lines):
        return address_lines[-1]

    @staticmethod
    def booth_number_in(booth_number_lines):
        for booth_number_line in booth_number_lines:
            booth_number_search = BOOTH_NUMBER_REGEX.search(booth_number_line)
            if booth_number_search:
                yield booth_number_search.group("booth_number")
