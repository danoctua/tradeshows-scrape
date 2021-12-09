import scrapy


class ExhibitorItem(scrapy.Item):

    _order = [
        "show_name",
        "show_date",
        "show_year",
        "show_website",
        "submitted_by",
        "exhibitor_name",
        "booth_number",
        "hall_location",
        "website",
        "email",
        "phone",
        "fax",
        "address",
        "country",
        "category",
        "manufacturers",
        "brands",
        "description",
    ]
    # These fields are populated automatically from the spider attributes and settings
    show_name = scrapy.Field(field_name="ShowName")
    show_date = scrapy.Field(field_name="ShowDate")
    show_year = scrapy.Field(field_name="ShowYear")
    show_website = scrapy.Field(field_name="ShowWebsite")
    submitted_by = scrapy.Field(field_name="SubmittedBy")

    exhibitor_name = scrapy.Field(field_name="ExhibitorName")
    booth_number = scrapy.Field(field_name="BoothNumber")
    hall_location = scrapy.Field(field_name="HallLocation")
    address = scrapy.Field(field_name="Address")
    country = scrapy.Field(field_name="Country")
    category = scrapy.Field(field_name="Categories")
    manufacturers = scrapy.Field(field_name="Manufacturers")
    brands = scrapy.Field(field_name="Brands")
    description = scrapy.Field(field_name="Description")
    # contact
    website = scrapy.Field(field_name="Website")
    email = scrapy.Field(field_name="Email")
    phone = scrapy.Field(field_name="Phone")
    fax = scrapy.Field(field_name="Fax")

    def get_order(self):
        """Method to get order of the fields that will be used in"""
        return self._order
