#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: The executor for crawler, should be called from cli
"""

import sys
import os.path
import inspect
import getopt
sys.path.insert(0, os.path.dirname(os.path.abspath(os.path.join(inspect.getfile(inspect.currentframe()), os.pardir))))

from crawler.worker.LinkCrawler import LinkCrawler
from crawler.db.MongoQueue import MongoQueue
from crawler.runner.CrawlJobRunner import CrawlJobRunner


def crawl_runner(site_root=None, max_depth=None, job_id=None):
    if job_id:
        job_runner = CrawlJobRunner(job_id)
        job_runner.run_job()
    else:
        queue = MongoQueue()
        #  This will clear the current cache so really risky for running executions
        queue.clear()
        link_crawler = LinkCrawler(site_root, queue=queue, max_depth=max_depth)
        link_crawler.threaded_executor()


def parse_args():
    site_root = None
    max_depth = None
    job_id = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:d:j:h:', ['site=', 'depth=', 'job=', 'help'])
    except getopt.GetoptError as err:
        print err
        print_help()

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print_help()
        elif opt in ('-s', '--site'):
            site_root = arg
        elif opt in ('-d', '--depth'):
            max_depth = int(arg)
            if max_depth > 4:
                print_help()
        elif opt in ('-j', '--job'):
            job_id = arg
        else:
            print_help()

    if site_root and max_depth:
        crawl_runner(site_root, max_depth)
    elif job_id:
        crawl_runner(job_id=job_id)
    else:
        print_help()

def print_help():
    print "-h, --help show this menu\n" \
          "-s, --site specify the site root to crawl(required)\n" \
          "-d, --depth specify the depth to crawl(required, less then 4)\n" \


    sys.exit(2)

if __name__ == '__main__':
    parse_args()
