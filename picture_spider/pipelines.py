# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os

import six

try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO

from PIL import Image
from urllib.parse import urlparse
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline, ImageException


class PicturePipeline(object):
    def process_item(self, item, spider):
        return item


class SavePicturePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        url = item['url']
        result = urlparse(url)

        yield Request(url=item['url'],
                      headers={
                          'Authority': result.netloc,
                          'Path': result.path,
                          'Scheme': result.scheme,
                          'DNT': 1,
                          'Referer': item['referer'],
                          'Upgrade-Insecure-Requests': 1
                      },
                      meta={'item': item})

    def item_completed(self, results, item, info):
        return item

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        file_name = self._get_file_name(item)
        return os.path.join('full', file_name)

    def thumb_path(self, request, thumb_id, response=None, info=None):
        item = request.meta['item']
        file_name = self._get_file_name(item)
        return os.path.join('thumbs', thumb_id, file_name)

    def get_images(self, response, request, info):
        path = self.file_path(request, response=response, info=info)
        orig_buf = BytesIO(response.body)
        orig_image = Image.open(orig_buf)

        width, height = orig_image.size
        if width < self.min_width or height < self.min_height:
            raise ImageException("Image too small (%dx%d < %dx%d)" %
                                 (width, height, self.min_width, self.min_height))

        yield path, orig_image, orig_buf

        image, buf = self.convert_image(orig_image)
        for thumb_id, size in six.iteritems(self.thumbs):
            thumb_path = self.thumb_path(request, thumb_id, response=response, info=info)
            thumb_image, thumb_buf = self.convert_image(image, size)
            yield thumb_path, thumb_image, thumb_buf

    @staticmethod
    def _get_file_name(item):
        img_name = os.path.basename(item['url'])
        file_ext = os.path.splitext(img_name)[1]

        real_name = item['name']
        page = str(item['page']).zfill(3)
        seq = str(item['seq']).zfill(2)

        return '%s-%s[%s]%s' % (page, seq, real_name, file_ext)
