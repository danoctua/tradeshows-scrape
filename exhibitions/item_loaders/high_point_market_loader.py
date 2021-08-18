from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
    join_loaded,
)


class HighPointMarketLoader(BaseItemLoader):
    @staticmethod
    def booth_number_out(booth_numbers):
        return join_loaded(booth_numbers, separator=",")
