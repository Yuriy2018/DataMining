# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import datetime

mongo_client = MongoClient()

class GbparsePipeline(object):
    def process_item(self, item, spider):
        now = datetime.datetime.now()
        database = mongo_client[spider.name]
        collection = database['instagram_parse_' + str(now.date())]
        collection.insert_one(item)
        return item
