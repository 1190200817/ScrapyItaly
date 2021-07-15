import scrapy
import re
import time
import logging
from pyquery import PyQuery
from ItalyInfo.items import ItalyInfoItem

logger = logging.getLogger(__name__)


class LarepubblicaSpider(scrapy.Spider):
    name = 'LaRepubblica'
    # allowed_domains = ['ricerca.repubblica.it/ricerca/repubblica?query=La+Belt+and+Road+Initiative']
    start_urls = ['https://ricerca.repubblica.it/ricerca/repubblica?query=La+Belt+and+Road+Initiative%2F']
    for i in range(2, 101):
        start_urls.append(start_urls[0] + '&page=' + str(i))

    def parse(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/47.0.2526.80 Safari/537.36 '
        }
        hrefList = response.css('a::attr(href)').extract()
        adjustHref = []
        for href in hrefList:
            newHref = href
            if href.startswith('//'):
                newHref = 'https:' + href
            if re.match(r'https://(\w)+(\.(\w)+)*(/\w+)*/\d{4}/\d{2}/\d{2}(/.+)+', newHref):
                adjustHref.append(newHref)

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
        # date = response.meta['date']
        title = html('h1').text()
        content = html('article p').text()
        author = html('article em').text()
        date = response.css('time::attr(datetime)').extract()

        logger.info("-----------------")
        logger.info(response.meta['url'])
        logger.info(title)
        logger.info(content)

        item = ItalyInfoItem()
        item['url'] = response.meta['url']
        item['source'] = "共和国报"
        item['title'] = title
        item['content'] = content
        item['author'] = author
        item['published_at'] = str(date[0]) + " 00:00:00"
        item['language'] = "it"
        yield item
