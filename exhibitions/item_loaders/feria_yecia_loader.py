from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader


class FeriaYeciaLoader(BaseItemLoader):

    @staticmethod
    def description_out(descriptions):
        return " ".join(descriptions)
