from typing import List

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader, join_loaded


class FurnitureManufacturerItemLoader(BaseItemLoader):

    @staticmethod
    def category_in(category_list: List[str]) -> str:
        # remove empty strings
        return join_loaded(category_list)

    @staticmethod
    def address_in(address_lines: List[str]) -> str:
        # remove empty strings
        return join_loaded(address_lines, ", ")
