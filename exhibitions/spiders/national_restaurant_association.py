import datetime
from exhibitions.spiders.base_spiders.base_map_your_show_spider import (
    BaseMapYourShowSpider,
)


class NationalRestaurantAssociationSpider(BaseMapYourShowSpider):
    name = "NationalRestaurantAssociationSpider"

    EXHIBITION_DATE = datetime.date(2022, 5, 21)
    EXHIBITION_NAME = "National Restaurant Association Show"
    EXHIBITION_WEBSITE = "https://restaurant.org/events-and-community/events-calendar/national-restaurant-association-show/"

    EXHIBITORS_LIST_API = "https://directory.nationalrestaurantshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorNames"
    EXHIBITOR_INFO_API = "https://directory.nationalrestaurantshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorBooths&exhID={exhibitor_id}"
    EXHIBITOR_BOOTHS_API = "https://directory.nationalrestaurantshow.com/8_0/exhview/exh-remote-proxy.cfm?action=getExhibitorBooths&exhID={exhibitor_id}"
