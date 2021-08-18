from exhibitions.item_loaders.base_item_loaders.base_item_loader import (
    BaseItemLoader,
    join_loaded,
)


class LasVegasMarketItemLoader(BaseItemLoader):
    @staticmethod
    def booth_number_out(booth_numbers):
        return join_loaded(booth_numbers, separator=",")

    @staticmethod
    def hall_location_out(hall_locations):
        return join_loaded(hall_locations, separator=",")
