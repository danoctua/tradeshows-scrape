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
        "description"
    ]
    # add field if you need more here
    show_name = scrapy.Field(field_name="ShowName")
    show_date = scrapy.Field(field_name="ShowDate")
    show_year = scrapy.Field(field_name="ShowYear")
    show_website = scrapy.Field(field_name="ShowWebsite")
    submitted_by = scrapy.Field(field_name="SubmittedBy")

    exhibitor_url = scrapy.Field()
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
    # social
    facebook = scrapy.Field(social=True)
    instagram = scrapy.Field(social=True)
    linkedin = scrapy.Field(social=True)
    twitter = scrapy.Field(social=True)

    def get_order(self):
        order = self._order
        return order
