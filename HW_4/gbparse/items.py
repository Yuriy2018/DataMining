# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


# title = response.xpath('//h1[@class="header"]/span').extract_first()
#          title =title.replace("<span>","")
#          title = title.replace("</span>", "")

def get_salary(valeues):
    return valeues

def dict_skils(values):
    result = {}
    for val in values.split('<li>'):
        result.update(val)

    return result

class GbparseItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field(output_processor=TakeFirst())
    url  = scrapy.Field(output_processor=TakeFirst())
    salary = scrapy.Field(input_processor=MapCompose(get_salary))
    keySkils  =    scrapy.Field(input_processor=MapCompose(dict_skils))
    organization = scrapy.Field(output_processor=TakeFirst())
    organization_url = scrapy.Field(output_processor=TakeFirst())
    organization_photo = scrapy.Field(output_processor=TakeFirst())

