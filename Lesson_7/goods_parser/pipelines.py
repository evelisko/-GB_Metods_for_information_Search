# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
from urllib.parse import urlparse
import re
import os


def get_charactercstic(items):
    charactercstics = {}
    names = items.xpath("//dt[@class='def-list__term']/text()").extract()
    values = items.xpath("//dd[@class='def-list__definition']/text()").extract()
    names = list(map(lambda x: x.strip(),names))
    values = list(map(lambda x: x.strip(),values))
    c = zip(names,values)
    for i in c:
        charactercstics[i[0]] = i[1]
    return charactercstics


class DataBasePipeline:  # Складываемсчитанные с сайта данные в БД.
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.goods_db

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        goods_atr = {}
        goods_atr['name'] = item['name']
        goods_atr['price'] = item['price']
        goods_atr['raiting'] = item['raiting']
        goods_atr['reviewCount'] = item['reviewCount']
        goods_atr['characteristics'] = get_charactercstic(item['characteristics'])
        goods_atr['url'] = item['url']
        collection.insert_one(goods_atr)
        return goods_atr

    def __del__(self):
        self.client.close()


class GoodsParserPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['picture']:
            for img in item['picture']:
                try:
                    img_path = img
                    yield scrapy.Request(img_path, meta=item)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        picture_name = request.url
        directory = re.findall(r'\d{6}', picture_name)[0]
        return f'full/{directory}/{os.path.basename(urlparse(picture_name).path)}'


    def item_completed(self, results, item, info):
        if results:
            item['picture'] = [itm[1] for itm in results if itm[0]]
        return item
