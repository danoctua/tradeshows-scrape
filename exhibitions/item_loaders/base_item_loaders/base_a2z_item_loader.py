from typing import List, Optional

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader


class BaseA2ZItemLoader(BaseItemLoader):
    @staticmethod
    def address_in(address_lines: List[Optional[str]]):
        return " ".join(a.strip() for a in address_lines if a)

    @staticmethod
    def category_in(categories: List[Optional[str]]):
        return " | ".join(c.strip() for c in categories if c)
