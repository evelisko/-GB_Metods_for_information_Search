# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
# from scrapy.loader.processors import MapCompose, TakeFirst


class GoodsParserItem(scrapy.Item):
    _id = scrapy.Field()
    name = scrapy.Field()
    picture = scrapy.Field()
    parameters = scrapy.Field()
    price = scrapy.Field()
    characteristics = scrapy.Field()
    url = scrapy.Field()



