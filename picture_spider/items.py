# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PictureItem(scrapy.Item):
    page = scrapy.Field()
    seq = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    referer = scrapy.Field()
