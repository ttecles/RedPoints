"""Usage: crawler.py [--timeout=<seconds>] RESOURCE INPUT

Collects data from a resource

Arguments:
    RESOURCE  resource to use. Right know, only GITHUB is implemented
    INPUT     JSON file input

Options:
    --timeout=<seconds> SEC  timeout used for fetching data
"""
import json
import os
import sys
from pprint import pprint

from docopt import docopt

from github_crawler import GitHubCrawler


def github_crawler(input_data, timeout):
    crawler = GitHubCrawler(input_data.get('proxies'), timeout=timeout)
    data = crawler.fetch_urls(input_data.get('keywords', None), input_data.get('type', None))
    return data


def main(argv):
    arguments = docopt(__doc__, argv=argv)

    file_input = arguments['INPUT']
    if not os.path.exists(file_input):
        raise ValueError("File not found")

    timeout = arguments['--timeout']
    if timeout:
        try:
            timeout = float(timeout)
        except:
            raise ValueError("Invalid timeout value")

    with open(file_input, 'r') as json_file:
        input_content = json.load(json_file)

    if arguments['RESOURCE'].lower() == 'github':
        data = github_crawler(input_content, timeout=timeout)
    else:
        data = None
    return data


if __name__ == '__main__':
    try:
        data = main(argv=sys.argv[1:])
    except Exception as e:
        sys.exit(str(e))
    else:
        pprint(data) if data else print("No data fetched")