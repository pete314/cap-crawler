#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: 29 Jan 2016
Description:  Manual test of LinkCrawler
"""

from crawler.worker.LinkCrawler import LinkCrawler
from crawler.db.MongoQueue import MongoQueue

def manual_test_LinkCrawler():
    sites = ["https://crosssec.com", "http://w5labs.hu", "http://www.gmit.ie"]
    for site in sites:
        queue = MongoQueue()
        queue.clear()
        link_crawler = LinkCrawler(site, queue=queue)
        results = link_crawler.process_list()
        for values in results:
            for link in values:
                print (link)

if __name__ == '__main__':
    manual_test_LinkCrawler()
