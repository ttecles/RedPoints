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
    --keyword KEYWORD   keywords to search for.
    --proxy PROXY       proxies to use.
    --type TYPE         type of repository to collect.
    --extra             extra information. Only valid on Repository type.

```

You can also import the GitHubCrawler and run the fetch_urls() method:

```python
from crawlers import GitHubCrawler

c = GitHubCrawler(["193.149.225.228:80", "3.25.29.231:3128"])
c.fetch_data(['dimensigon'], type="Repositories", extra=True)
```