# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import time
import logging
import uuid
import pymongo
import re

logger = logging.getLogger(__name__)


class ItalyInfoPipeline:
    collection_name = 'ItalyInfo'

    def process_item(self, item, spider):
        return item

    def __init__(self, settings):
        self.settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings, )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(host=self.settings['MONGODB_HOST'], port=self.settings['MONGODB_PORT'])
        self.db = self.client[self.settings['MONGODB_DB']]
        self.collection = self.db[self.collection_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        item['task_id'] = os.environ.get('CRAWLAB_TASK_ID')
        item['_id'] = str(uuid.uuid3(uuid.NAMESPACE_DNS, item['url']))
        item['created_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        item['status'] = 0
        item['zh_title'] = ''
        item['zh_content'] = ''
        if not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', item['published_at']):
            logger.info('[Process item] published_at invalid format, published_at={}'.format(item['published_at']))
            return
        if item['title'] and item['content'] and item['published_at']:
            item_ = self.collection.find_one({'_id': item['_id']})
            if item_:
                # self.collection.update_one({'_id': item['_id']}, {"$set": {"published_at": item['published_at']}})
                logger.info('[Process item] data is exists, title={}, url={}'.format(item['title'], item['url']))
            else:
                self.collection.insert_one(dict(item))
                logger.info('[Process item] data has saved, title={}, url={}'.format(item['title'], item['url']))
                return item
        else:
            logger.info(
                '[Process item] miss title or content, title={}, url={}'.format(item['title'], item['url']))
