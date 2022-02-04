import datetime
import json
from typing import Optional

from exhibitions.spiders.base_spiders.base_algolia_spider import BaseAlgoliaSpider


class NationalHardwareShowSpider(BaseAlgoliaSpider):
    name = "NationalHardwareShowSpider"

    EXHIBITION_DATE = datetime.date(2022, 4, 5)
    EXHIBITION_NAME = "National Hardware Show"
    EXHIBITION_WEBSITE = "https://www.nationalhardwareshow.com/"

    HEADERS = {}  # replace with headers dict

    BASE_URL = "https://xd0u5m6y4r-dsn.algolia.net/1/indexes/event-edition-eve-e6b1ae25-5b9f-457b-83b3-335667332366_en-us/query?x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%203.27.1&x-algolia-application-id=XD0U5M6Y4R&x-algolia-api-key=d5cd7d4ec26134ff4a34d736a7f9ad47"
    URLS = [BASE_URL]

    def _get_payload_body(self, page: Optional[int] = None) -> str:
        if page is None:
            page = 0

        body = {"params": f"page={page}"}
        print(json.dumps(body))
        return json.dumps(body)
