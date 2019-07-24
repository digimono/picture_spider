# -*- coding: utf-8 -*-

from scrapy import cmdline


def main():
    name = 'macapp_so_spider'
    cmd = 'scrapy crawl {0}'.format(name)
    cmdline.execute(cmd.split())


if __name__ == '__main__':
    main()
