# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class ItalyInfoItem(scrapy.Item):
    task_id = scrapy.Field()  # crawlab任务id（自动生成）
    _id = scrapy.Field()  # id 根据url生成，用于去重（自动生成）
    title = scrapy.Field()  # 标题
    content = scrapy.Field()  # 正文
    published_at = scrapy.Field()  # 网站发布时间（格式: 2021-06-24 00:00:00）
    language = scrapy.Field()  # 语种（ru/en/ja/ko）
    author = scrapy.Field()  # 作者
    source = scrapy.Field()  # 来源网站（网站中文正式名称）
    url = scrapy.Field()  # url地址
    created_at = scrapy.Field()  # 入库时间（自动生成）
    status = scrapy.Field()  # 状态（自动生成）
    zh_title = scrapy.Field()  # 翻译后中文标题（后续脚本翻译）
    zh_content = scrapy.Field()  # 翻译后中文正文（后续脚本翻译）
