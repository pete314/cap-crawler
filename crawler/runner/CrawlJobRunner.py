#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Extract crawl job params from db entry and run
"""

import atexit
from crawler.db.CassandraWrapper import CassandraWrapper
from crawler.worker.LinkCrawler import LinkCrawler

CAP_DATA_KS = 'capdata'

class CrawlJobRunner(object):
    def __init__(self, job_id):
        self.job_id = job_id
        self.Cassa = CassandraWrapper(CAP_DATA_KS)
        self._clenup = self.close
        atexit.register(self._clenup)  # If collapse or ctrl-c c* session will be closed

    def close(self):
        self.Cassa.close()

    def run_job(self):
        """
        Currently just processing link_crawl, with max depth of 3
        :return:
        """
        job = self.Cassa.get_job(self.job_id)

        if job is not None:
            job_id, has_depth, job_type, recurrance, startin_params, user_id = job

            depth = has_depth if isinstance(has_depth, int) and int(has_depth) < 4 else 3
            site_root = None
            start_at = None

            startin_bits = startin_params.split(',')
            for b in startin_bits:
                if "site-root" in b:
                    site_root = b.split("site-root:", 1)[1]
                elif "start-at-page" in b:
                    start_at = b.split("start-at-page:", 1)[1]

            lc = LinkCrawler(site_domain=site_root, start_at=start_at, max_depth=depth)
            if lc.threaded_executor():
                self.Cassa.update_job_ready(self.job_id)
                print '\n+++++++++Done'
            else:
                self.Cassa.update_job_ready(self.job_id, status='ERROR - retry at recurrence')
                print '\n+++++++++Finished with errors'

            # Notify user about the outcome
        else:
            print '\n+++++++++Job can not be found'
