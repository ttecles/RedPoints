import re

import pytest
import responses

from github_crawler import GitHubCrawler
from tests.html_response import repo_response


@pytest.fixture
def input_request():
    return {
        "keywords": [
            "openstack",
            "nova",
            "css"
        ],
        "proxies": [
            "194.126.37.94:8080",
            "13.78.125.167:8080"
        ],
        "type": "Repositories"
    }


@responses.activate
def test_GithubCrawler(input_request):
    responses.add(responses.GET, re.compile(GitHubCrawler.BASE_URL + '.*'), body=repo_response, status=200)

    crawler = GitHubCrawler(input_request['proxies'])
    result = crawler.fetch_urls(input_request['keywords'], input_request['type'])
    assert result == [
        {
            "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage"
        },
        {
            "url": "https://github.com/michealbalogun/Horizon-dashboard"
        }
    ]
