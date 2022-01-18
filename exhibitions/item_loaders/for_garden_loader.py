from itemloaders.processors import TakeFirst

from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
)


class ForGardenItemLoader(BaseItemLoader):
    @staticmethod
    def country_out(country_lines):
        return TakeFirst()(reversed(country_lines))
