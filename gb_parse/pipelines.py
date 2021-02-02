# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class SaveToMongo:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client['gb_parse_12_01_2021']

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item