import scrapy


class ExhibitorItem(scrapy.Item):
    # add field if you need more here
    exhibition_name = scrapy.Field()
    exhibition_date = scrapy.Field()
    exhibition_website = scrapy.Field()

    exhibitor_url = scrapy.Field()
    exhibitor_name = scrapy.Field()
    booth_number = scrapy.Field()
    hall_location = scrapy.Field()
    address = scrapy.Field()
    country = scrapy.Field()
    category = scrapy.Field()
    manufacturers = scrapy.Field()
    brands = scrapy.Field()
    description = scrapy.Field()
    # contact
    website = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()
    fax = scrapy.Field()
    # social
    facebook = scrapy.Field(social=True)
    instagram = scrapy.Field(social=True)
    linkedin = scrapy.Field(social=True)
    twitter = scrapy.Field(social=True)
