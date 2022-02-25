# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaParserItem(scrapy.Item):
    current_user_name = scrapy.Field()
    current_user_id = scrapy.Field()
    follow_id = scrapy.Field()
    follow_name = scrapy.Field()
    follow_full_name = scrapy.Field()
    follow_pic_url = scrapy.Field()
    follow_user_type = scrapy.Field()
    # post = scrapy.Field()
