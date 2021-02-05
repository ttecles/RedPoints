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
    try:
        data = crawler.fetch_urls(input_data.get('keywords', None), input_data.get('type', None))
    except Exception as e:
        sys.exit(e)
    pprint(data)


if __name__ == '__main__':
    arguments = docopt(__doc__)

    file_input = arguments['INPUT']
    if not os.path.exists(file_input):
        sys.exit("File not found")

    timeout = arguments['--timeout']
    if timeout:
        try:
            timeout = float(timeout)
        except:
           sys.exit("Invalid timeout value")

    try:
        with open(file_input, 'r') as json_file:
            input_content = json.load(json_file)
    except json.decoder.JSONDecodeError as e:
        sys.exit(f"JSON parse error {file_input}. {e}")
    except Exception as e:
        sys.exit(str(e))

    if arguments['RESOURCE'].lower() == 'github':
        github_crawler(input_content, timeout=timeout)