import datetime

from exhibitions.item_loaders.base_item_loaders.base_item_loader import BaseItemLoader
from exhibitions.spiders.base_spiders.base_algolia_spider import BaseAlgoliaSpider


class MaisonObjetSpider(BaseAlgoliaSpider):
    name = "MaisonObjetSpider"

    EXHIBITION_DATE = datetime.date(2022, 3, 23)
    EXHIBITION_NAME = "Maison & Objet - January"
    EXHIBITION_WEBSITE = "https://www.maison-objet.com/en/paris/exhibitors"

    URLS = [
        "https://lpn4stglqg-dsn.algolia.net/1/indexes/*/queries?"
        "x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%3B%20instantsearch.js%20(3.7.0)%3B%20JS%20Helper%20(2.28.0)"
        "&x-algolia-application-id=LPN4STGLQG"
        "&x-algolia-api-key=3dfb0b32b6d93bd5a34dceabcc437108",
    ]
