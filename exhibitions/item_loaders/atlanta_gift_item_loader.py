from typing import List, Optional

from exhibitions.item_loaders.base_item_loader import BaseItemLoader, join_loaded


class AtlantaGiftItemLoader(BaseItemLoader):

    @staticmethod
    def booth_number_in(booth_numbers: List) -> Optional[str]:
        return join_loaded(booth_numbers)

    @staticmethod
    def phone_in(phone_number_parts: List) -> Optional[str]:
        return join_loaded(phone_number_parts, "-")

    @staticmethod
    def fax_in(fax_number_parts: List) -> Optional[str]:
        return join_loaded(fax_number_parts, "-")
