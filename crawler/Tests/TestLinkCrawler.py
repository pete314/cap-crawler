#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: LinkCrawler Test case
"""

import unittest
from crawler.worker.LinkCrawler import LinkCrawler

class MyTestCase(unittest.TestCase):
    def test_threaded_executor(self):
        link_crawler = LinkCrawler('https://crosssec.com', max_depth=1)
        result = link_crawler.threaded_executor()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
