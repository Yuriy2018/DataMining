# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

mongo_client = MongoClient()

class AvitoParsePipeline(object):
    def process_item(self, item, spider):
        database = mongo_client[spider.name]
        collection = database['avito_apartments']
        collection.insert_one(item)
        return item
