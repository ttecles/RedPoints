# GitHub Crawler

```shell
$ python crawler.py --help
Usage: crawler.py [--timeout SECONDS] [--keyword KEYWORD]... [--proxy PROXY]...
                     [--type TYPE] [--extra] [INPUT]

Collects data from a resource.

Arguments:
    INPUT     JSON file input

Options:
    --timeout SECONDS   SEC  timeout used for fetching data.
    --keyword KEYWORD   a list of keywords to be used as search terms
    --proxy PROXY       one of them is selected and used randomly to perform all the HTTP requests
                        (you can get a free list of proxies to work with at https://free-proxy-list.net/)
    --type TYPE         the type of object we are searching for (Repositories, Issues and Wikis supported)
    --extra             extra information. Only valid on Repositories type.

```

You can also import the GitHubCrawler and run the fetch_urls() method:

```python
from crawlers import GitHubCrawler

c = GitHubCrawler(["193.149.225.228:80", "3.25.29.231:3128"])
c.fetch_data(['dimensigon'], type="Repositories", extra=True)
```