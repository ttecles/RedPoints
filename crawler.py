"""Usage: crawler.py [--timeout SECONDS] [--keyword KEYWORD]... [--proxy PROXY]...
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
"""
import json
import os
import sys
from pprint import pprint

from docopt import docopt

from github_crawler import GitHubCrawler


def github_crawler(keywords, proxies, type, timeout=None, extra=False):
    crawler = GitHubCrawler(proxies, timeout=timeout)
    data = crawler.fetch_urls(keywords, type, extra)
    return data


def main(argv):
    arguments = docopt(__doc__, argv=argv)

    timeout = arguments['--timeout']
    if timeout:
        try:
            timeout = float(timeout)
        except:
            raise ValueError("Invalid timeout value")

    file_input = arguments['INPUT']
    if file_input:
        if not os.path.exists(file_input):
            raise FileNotFoundError("File not found")

        with open(file_input, 'r') as json_file:
            input_content = json.load(json_file)
    else:
        input_content = {'keywords': [], 'proxies': [], 'type': None}

    if arguments['--keyword']:
        input_content.update(keywords=arguments['--keyword'])
    if arguments['--proxy']:
        input_content.update(proxies=arguments['--proxy'])
    if arguments['--type']:
        input_content.update(type=arguments['--type'])
    if not input_content['type']:
        input_content['type'] = GitHubCrawler.TYPES[0]
    return github_crawler(**input_content, timeout=timeout, extra=arguments['--extra'])



if __name__ == '__main__':
    try:
        data = main(argv=sys.argv[1:])
    except Exception as e:
        sys.exit(str(e))
    else:
        pprint(data) if data else print("No data fetched")