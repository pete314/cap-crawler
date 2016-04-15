#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Author: Peter Nagy
Since: Jan 2016
Description: Wrapper class for cassandra db
"""

"""
 create table html_dump ( block_uid uuid primary key, site_domain varchar, site_url varchar, content text, created timestamp);
 create keyspace crawl_dump with replication = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };

"""

from cassandra.cluster import Cluster

class CassandraWrapper(object):
    def __init__(self, host='localhost', port='9160'):
        """
        Initialize the connection
        :param host:
        :param port:
        :return:
        """
        self.cluster = Cluster()#connects on localhost
        self.session = self.cluster.connect('crawl_dump')

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
            self.session.execute(prep.bind(params_dict))
        elif column_family is 'crawled_links' and len(params_dict) is 4:
            self.session.execute(
                """
                delete from crawled_links where url_hash = %(url_hash)s
                """,
                params_dict
            );
            self.session.execute(
                """
                insert into crawled_links(url_hash, url, crawler_job, created)
                values (%(url_hash)s, %(url)s, %(crawler_job)s, %(created)s)
                """,
                params_dict
                )
        else:
            return None
