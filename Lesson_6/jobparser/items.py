# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

# import scrapy
#
#
# class JobparserItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass
#
import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    salary = scrapy.Field()
    experience = scrapy.Field()
    skils = scrapy.Field()
    company_name = scrapy.Field()
    company_href = scrapy.Field()
    company_location = scrapy.Field()
    publication_date = scrapy.Field()
    connection_info = scrapy.Field()