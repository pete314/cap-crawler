CAP crawler
===
A simple python crawler with threaded execution and shared execution queue.

**Introduction**
----
The project was created for research purposes to collect structured and unstructured data from the web. Collected data is stored in [Cassandra](http://www.planetcassandra.org/cassandra/) for scaling purposes and to increase IO.

**Features**
----
 - Shared crawl execution queue with MongoDb
 - Link & content scraping options
 - Robot.txt checking, to avoid unwanted crawling
 - Download error checking and retry
 - Cli execution


----------


**Dependencies**
----
[Python 2.7](https://www.python.org/download/releases/2.7/) is the version the application is written in.
[MongoDb](https://www.mongodb.org/) version > 3.0. For install instruction please visit [the official site](https://docs.mongodb.org/manual/administration/install-community/), which contains easy to follow working instructions not only on installation.
Cassandra with [cql v.3](https://cassandra.apache.org/doc/cql3/CQL-2.2.html), I used the Datastax community version 3, but the Apache version is fine as well. Install instruction are available [here](http://docs.datastax.com/en/cassandra/3.x/cassandra/install/installDeb.html).

#####Python modules:
```
pip install cassandra-driver
pip install pymongo
pip install bs4
pip install lxml
```

**Database structures**
--------------------
 **Mongo** is only used as a queue to make threaded execution easier, so there isn't really a structure as such.
 A link in cache contains 4 properties:
 **_id**: is the url itslef
**status**:  the status of the entry (waiting | processing | complete)
 **depth**: the depth where the content will be scraped
 **timestamp**: the last access time

**Cassandra**
The setup may differ from the use case. I suggest to run it trough cqlsh.
```Sql
-- Single node configuration
-- Create keyspace for crawl dump
create keyspace CrawlDump with replication = {'class': 'SimpleStrategy', 'replication_factor' : 1};
use CrawlDump;
-- Create tables for crawl dump with extra indexes to avoid filtering
create table crawl_dump (url_hash text primary key, content blob, crawler_job text, created timestamp, scrape_type text, url text);
-- Search is performed on crawler_job so crate an index
create index on CrawlDump.crawl_dump (crawler_job);
create table crawled_links(url_hash text primary key, crawler_job text, status varchar, message varchar, created timestamp, url text);
-- Search is performed on crawler_job so crate an index
create index on CrawlDump.crawled_links (crawler_job);
```


**Execution**
---

 1. **Download**, clone the repository
 2. Open command prompt or cli and navigate to **/path/to/repo/crawler/**
 3. Either make **cap_runner.py** executable and call it trough bash (sh or **./cap_runner.py**) or simply  execute it with **python cap_runner.py** as a script.

#### Command line arguments
```
-h, --help 	show options
-s, --site 	specify the site root to crawl(required)
-d, --depth specify the depth to crawl(required, less then 4)
-j, --job 	hex id generated for predefined parameters for execution
```

##### Execution examples
```
Execute a pre-configured execution job
./cap_runner.py --job 'HEX_PRE_SPECIFIED_JOB_ID'
Quick run
./cap_runner.py --site 'https://example.com' --depth 3
```




Notes
-----

There is a limit for **maximum depth** which is **4**, even with unique link visits its is possible to visit 100K pages or even more if the site is large. The start_at parameter can come in handy to reach different parts of a large site.
By default the **entire page content is stored** in c* so large crawling sessions require sufficient storage.
By default only html content is processed.
Different crawling jobs can overwrite links found, as the id is hash based, for easier management and to avoid duplicate links.

##Known issues
Urls/robot content with special characters are not parsed.


##References
[Python 2.7](https://www.python.org/download/releases/2.7/)
[MongoDb](https://www.mongodb.org/)
[Mongo install instructions ](https://docs.mongodb.org/manual/administration/install-community/)
[Cql v.3 reference manual](https://cassandra.apache.org/doc/cql3/CQL-2.2.html)
[Datastax Cassandra install instructions](http://docs.datastax.com/en/cassandra/3.x/cassandra/install/installDeb.html)
[Web Scraping with Python - amazon.com](http://www.amazon.com/Web-Scraping-Python-Richard-Lawson-ebook/dp/B00YSIL1XK)

##Disclaimer

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
