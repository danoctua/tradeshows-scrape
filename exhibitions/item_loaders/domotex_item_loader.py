from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
)


class DomotexItemLoader(BaseItemLoader):
    @staticmethod
    def country_out(address_lines):
        return address_lines[-1]
