# -*- coding: utf-8 -*-ArticleLstBox

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

import json
class BishijiePipeline(object):

    def process_item(self, item, spider):

        with open("b3.txt", "a", encoding="utf-8") as f:

            f.write(json.dumps(item, ensure_ascii=False, indent=2))
            print("保存成功")


        return item


 # def open_spider(self,spider):
    #     client=MongoClient("127.0.0.1",27017)
        # self.collection.insert(item)
    #     self.collection=client[][]