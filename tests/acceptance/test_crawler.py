import ast
import os
import shlex
import sys

import pytest
import responses
from io import StringIO

from crawler import main
from github_crawler import GitHubCrawler
from tests.html_response import expected_repo_urls, repo_response

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@responses.activate
def test_crawler():
    responses.add(responses.GET, GitHubCrawler.BASE_URL + '/search?q=openstack+nova+css&type=Repositories',
                  body=repo_response, status=200)
    data = main(shlex.split(f"--timeout 20  github {os.path.join(BASE_DIR, 'input1.json')} "))

    assert expected_repo_urls == data

@responses.activate
def test_crawler_invalid_timeout():
    with pytest.raises(ValueError) as e:
        main(shlex.split(f"--timeout x  github {os.path.join(BASE_DIR, 'input1.json')} "))


@responses.activate
def test_crawler_invalid_file():
    with pytest.raises(ValueError) as e:
        main(shlex.split(f"--timeout x  github xxx"))