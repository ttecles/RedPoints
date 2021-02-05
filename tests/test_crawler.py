import os
import shlex
from unittest.mock import patch

import httpx
import pytest
import respx

from crawler import main
from crawlers import GitHubCrawler
from tests.html_response import expected_repo_urls, repo_response

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.acceptance()
@respx.mock
def test_crawler_main():
    respx.get(GitHubCrawler.BASE_URL + '/search?q=openstack+nova+css&type=Repositories').mock(
        return_value=httpx.Response(200, html=repo_response))
    data = main(shlex.split(f"{os.path.join(BASE_DIR, 'input.json')}"))

    assert expected_repo_urls == data


@pytest.mark.acceptance()
@patch('crawler.crawlers')
def test_crawler_main_parameters(mock_github_crawler):
    main(shlex.split(
        f"--timeout 20 --keyword openstack --keyword nova --keyword css --proxy 193.149.225.228:80 --extra"))

    mock_github_crawler.assert_called_once_with(keywords=['openstack', 'nova', 'css'], proxies=['193.149.225.228:80'],
                                                type=GitHubCrawler.TYPES[0], timeout=20, extra=True)


@pytest.mark.acceptance
@patch('crawler.crawlers')
def test_crawler_main_parameters_with_type(mock_github_crawler):
    main(shlex.split(
        f"--type Wikis"))

    mock_github_crawler.assert_called_once_with(keywords=[], proxies=[],
                                                type='Wikis', timeout=None, extra=False)


def test_crawler_main_invalid_timeout():
    with pytest.raises(ValueError):
        main(shlex.split(f"--timeout x"))


def test_crawler_main_invalid_file():
    with pytest.raises(FileNotFoundError):
        main(shlex.split(f"x"))
