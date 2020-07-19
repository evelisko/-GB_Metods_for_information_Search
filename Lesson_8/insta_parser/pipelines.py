# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient


class InstaParserPipeline(object):

    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.mongo_base = self.client.instagram_users_db

    def process_item(self, item, spider):
        collection = self.mongo_base[item['follow_user_type']]
        user_art = {}
        user_art['current_user_name'] = item['current_user_name']
        user_art['current_user_id'] = item['current_user_id']
        user_art['follow_id'] = item['follow_id']
        user_art['follow_name'] = item['follow_name']
        user_art['follow_full_name'] = item['follow_full_name']
        user_art['follow_pic_url'] = item['follow_pic_url']
        user_art['follow_user_type'] = item['follow_user_type']
        # user_art['post'] = item['post']
        collection.insert_one(user_art)
        return user_art

    def __del__(self):
        self.client.close()
