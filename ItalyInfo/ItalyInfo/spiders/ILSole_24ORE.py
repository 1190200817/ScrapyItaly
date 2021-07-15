import scrapy
import re
import logging
from pyquery import PyQuery
from ItalyInfo.items import ItalyInfoItem

logger = logging.getLogger(__name__)


class Ilsole24oreSpider(scrapy.Spider):
    name = 'ILSole_24ORE'
    # allowed_domains = ['abc']
    start_urls = ['https://www.ilsole24ore.com/archivi/']
    for j in range(1, 207):
        start_urls.append(start_urls[0] + str(j))

    def parse(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/47.0.2526.80 Safari/537.36 '
        }
        hrefList = response.css('a::attr(href)').extract()
        adjustHref = []
        for href in hrefList:
            if href.startswith('/'):
                href = 'https://www.ilsole24ore.com' + href
                if re.match(r'https://www\.ilsole24ore\.com/art/.+', href):
                    adjustHref.append(href)

        for href in adjustHref:
            try:
                request = scrapy.Request(href, callback=self.parse_info, headers=headers)
                request.meta["url"] = href
                yield request
            except:
                continue

    def parse_info(self, response):
        """解析新闻详情"""
        html = PyQuery(response.text)
        href = response.meta['url']
        date = response.css('time::attr(datetime)').extract()
        title = html('h1[class^=atitle]').text()
        content = html('p[class^=atext]').text()
        author = html('p[class^=auth]').text()

        logger.info("-----------------")
        logger.info(response.meta['url'])
        logger.info(title)
        logger.info(content)

        item = ItalyInfoItem()
        item['url'] = response.meta['url']
        item['source'] = "意大利24小时太阳报"
        item['title'] = title
        item['content'] = content
        item['author'] = author
        item['published_at'] = date[0] + " 00:00:00"
        item['language'] = "it"
        yield item
