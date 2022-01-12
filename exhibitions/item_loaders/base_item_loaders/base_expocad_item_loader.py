from itemloaders.processors import Join

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader


class BaseExpocadItemLoader(BaseItemLoader):

    booth_number_out = Join(", ")
