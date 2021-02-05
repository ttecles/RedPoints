import ast
import os
import shlex
import sys

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
    result = StringIO()
    sys.stdout = result
    main(shlex.split(f"--timeout 20  github {os.path.join(BASE_DIR, 'input1.json')} "))

    assert expected_repo_urls == ast.literal_eval(result.getvalue())
