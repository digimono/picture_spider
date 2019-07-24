# -*- coding: utf-8 -*-


import logging

from scrapy import Request
from scrapy.exceptions import CloseSpider
from scrapy.spiders import Spider

from picture_spider.items import PictureItem
from picture_spider.util.time_util import Wait

logger = logging.getLogger(__name__)


class MacAppSoSpider(Spider):
    name = 'macapp_so_spider'
    allowed_domains = ['macapp.so']
    start_urls = ['https://www.macapp.so/wallpaper/index.html']

    def parse(self, response):
        links = response.css('div.wallpaper ul li h2 a')
        page_links = response.css('div.wallpaper div.page a')
        page = response.css('div.wallpaper div.page').xpath('./b/text()').extract_first()

        if len(links) == 0:
            logger.warning('Image crawl failed')
            raise CloseSpider('Image crawl failed')

        for index, link in enumerate(links):
            name = link.xpath('string()').extract_first()
            href = link.xpath('@href').extract_first()
            next_url = response.urljoin(href)

            # args = (str(index + 1).zfill(2), name, next_url)
            # logger.debug('Image #%s: name %s, url %s' % args)

            item = PictureItem()
            item['page'] = int(page)
            item['seq'] = index + 1
            item['name'] = name
            item['referer'] = next_url

            Wait.wait_seconds(1, 3)
            yield Request(next_url, meta={'item': item}, callback=self.parse_raw_image)

        next_link = list(page_links)[-2]
        name = next_link.xpath('string()').extract_first()
        href = next_link.xpath('@href').extract_first()
        next_url = response.urljoin(href)

        if name == '下一页':
            yield Request(next_url, callback=self.parse)
        else:
            logger.error('Gets next page failed')

    def parse_raw_image(self, response):
        img = response.css('div.bimg p a img')
        src = img.xpath('@src').extract_first()
        name = img.xpath('@alt').extract_first()

        logger.debug('Image: alt %s, url %s' % (name, src))

        item = response.meta['item']
        item['name'] = name
        item['url'] = src

        yield item
