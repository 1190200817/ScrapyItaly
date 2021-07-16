import logging
import time
import uuid
import argparse
import hashlib
import requests
import pymongo

from functools import lru_cache


logging.basicConfig(format='[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s] %(message)s', level='INFO')
logger = logging.getLogger(__name__)


class BaiduTranslate(object):
    """调用百度翻译API"""

    def __init__(self, conf: dict):
        self.appid = conf['appid']
        self.password = conf['password']
        self.salt = conf['salt']
        self.url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    @lru_cache()
    def get_sign(self, text: str):
        """生成签名"""

        key = '{}{}{}{}'.format(self.appid, text, self.salt, self.password)
        sign = hashlib.md5(key.encode('utf-8')).hexdigest()
        return sign

    @lru_cache()
    def translate(self, text: str, to_lang: str):
        """调用API翻译"""

        time.sleep(0.9)
        text_ = text.replace('\n', ' ')
        data = {
            'q': text_,
            'from': 'auto',
            'to': to_lang,
            'appid': self.appid,
            'salt': self.salt,
            'sign': self.get_sign(text_)
        }
        response = requests.post(self.url, headers=self.headers, data=data, timeout=120)
        logger.info('[Baidu translate] response={}'.format(response))
        if response.status_code == 200:
            result = response.json()
            logger.info('result={}'.format(result))
            if 'error_code' in result:
                logger.error('[Baidu translate] serve error, {}'.format(response.text))
                time.sleep(5)
            else:
                data = {
                    'from': result['from'],
                    'to': result['to'],
                    'src': result['trans_result'][0]['src'],
                    'dst': result['trans_result'][0]['dst']
                }
                return data
        else:
            logger.error('[Baidu translate] serve error, {}'.format(response.text))


class ItalyInfoTranslate(object):
    """翻译数据"""

    def __init__(self, conf: dict):
        self.translator = BaiduTranslate(conf['baidu'])
        self.client = pymongo.MongoClient(conf['mongodb']['host'])
        self.collection = self.client[conf['mongodb']['table']][conf['mongodb']['collection']]

    def handle(self):
        count = 0
        query = {'status': 0}
        while True:
            if self.collection.count_documents(query) == 0:
                break
            documents = self.collection.find({'status': 0}).sort('published_at', pymongo.DESCENDING)[0: 100]
            for document in documents:
                count += 1
                trans_title = self.translator.translate(document['title'], 'zh')
                trans_content = self.translator.translate(document['content'], 'zh')
                if trans_title and trans_content:
                    data = {'status': 1, 'zh_title': trans_title['dst'], 'zh_content': trans_content['dst']}
                    self.collection.update_one({'_id': document['_id']}, {'$set': data})
                    logger.info('count={}, id={}'.format(count, document['_id']))


def main(args):
    util = ItalyInfoTranslate(args.conf)
    util.handle()


if __name__ == '__main__':
    conf = {
        'baidu': {
            'appid': '20210714000887983',
            'password': 'm0kLLH4o0HgWKLLKDYvC',
            'salt': '1435660288'
        },
        'mongodb': {
            'host': 'localhost',
            'table': 'Italy',
            'collection': 'ItalyInfo'
        }
    }
    parser = argparse.ArgumentParser()
    parser.add_argument('--conf', default=conf)
    args = parser.parse_args()
    main(args)
