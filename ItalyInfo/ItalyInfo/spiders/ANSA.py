import scrapy
import re
import logging
from pyquery import PyQuery
from ItalyInfo.items import ItalyInfoItem

logger = logging.getLogger(__name__)


class AnsaSpider(scrapy.Spider):
    name = 'ANSA'
    # allowed_domains = ['abc']
    start_urls = ['https://www.ansa.it/']
    appendix = ['cronaca/cronaca.shtml', 'politica/politica.shtml', 'economia/economia.shtml', 'mondo/mondo.shtml',
                'cultura/cultura.shtml', 'tecnologia/tecnologia.shtml', 'sport/sport.shtml']
    for i in range(len(appendix)):
        appendix[i] = 'sito/notizie/' + appendix[i]

    for i in appendix:
        start_urls.append(start_urls[0] + i)

    def parse(self, response):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/47.0.2526.80 Safari/537.36 '
        }
        hrefList = response.css('a::attr(href)').extract()
        adjustHref = []
        for href in hrefList:
            if href.startswith('/'):
                href = 'https://www.ansa.it' + href
            if re.match(r'https://www\.ansa\.it(/\w+)+/(2020|2021)/\d{2}/\d{2}/.+\.html', href):
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
        dateString = str(re.findall(r'\d{4}/\d{2}/\d{2}', href)[0])
        dateString = dateString.replace('/', '-')
        title = html('article h1').text()
        content = html('article p').text()
        author = html('article span[class^=news-author]').text()

        logger.info("-----------------")
        logger.info(response.meta['url'])
        logger.info(title)
        logger.info(content)

        item = ItalyInfoItem()
        item['url'] = response.meta['url']
        item['source'] = "意大利安莎通讯社"
        item['title'] = title
        item['content'] = content
        item['author'] = author
        item['published_at'] = str(dateString) + " 00:00:00"
        item['language'] = "it"
        yield item

