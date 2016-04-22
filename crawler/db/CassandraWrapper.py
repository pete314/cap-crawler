#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Wrapper class for cassandra db
"""
from datetime import datetime
from cassandra.cluster import Cluster


class CassandraWrapper(object):
    def __init__(self, host='localhost', port='9160', key_space='crawldump'):
        """
        Initialize the connection
        :param host:
        :param port:
        :return:
        """
        self.cluster = Cluster()  # Connects on localhost
        self.session = self.cluster.connect(key_space)

    def close(self):
        self.session.cluster.shutdown()
        self.session.shutdown()

    def insert_into(self, column_family, params_dict={}):
        if column_family is 'crawl_dump' and len(params_dict) is 6:
            self.session.execute(
                """
                delete from crawl_dump where url_hash = %(url_hash)s
                """,
                params_dict
            )  # Workaround for sql replace into
            prep = self.session.prepare(
                    """insert into crawl_dump (url_hash, url, scrape_type, crawler_job, content, created)
                        values (?, ?, ?, ?, ?, ?)
                    """)
            self.session.execute_async(prep.bind(params_dict))
        elif column_family is 'crawled_links' and len(params_dict) is 4:
            self.session.execute(
                """
                delete from crawled_links where url_hash = %(url_hash)s
                """,
                params_dict
            )
            self.session.execute_async(
                """
                insert into crawled_links(url_hash, url, crawler_job, created)
                values (%(url_hash)s, %(url)s, %(crawler_job)s, %(created)s)
                """,
                params_dict
                )
        else:
            return None

    def get_job(self, job_id):
        """"Get job from capdata.crawl_job inserted by API"""
        job = self.session.execute(
            """
            select job_id, has_depth, job_type, recurrance, startin_params, user_id
            from capdata.crawl_job
            where job_id = %(job_id)s
            """,
            {'job_id': job_id}
        )
        if len(job.current_rows) > 0:
            prep = self.session.prepare(
                """update capdata.crawl_job set status='IN QUEUE', started=?
                    where job_id = ?
                """)
            self.session.execute(prep.bind({'started': datetime.now(), 'job_id':job_id}))
            return job[0]  # Should return a single row
        else:
            return None

    def update_job_ready(self, job_id, status='READY'):
        """Update job in capdata.crawl_job """
        prep = self.session.prepare(
            """update capdata.crawl_job set status=?, finished=?
                where job_id = ?
            """)
        # Just dump the results, not waiting for response
        self.session.execute_async(prep.bind({'finished': datetime.now(), 'status': status, 'job_id': job_id}))
