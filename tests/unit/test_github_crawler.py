import re

import pytest
import responses

from github_crawler import GitHubCrawler
from tests.html_response import repo_response, issues_response, wikis_response, expected_repo_urls, \
    expected_issues_urls, expected_wikis_urls


@pytest.fixture
def keywords():
    return ["openstack", "nova", "css"]


@pytest.fixture
def proxies():
    return [
        "194.126.37.94:8080",
        "13.78.125.167:8080"
    ]


@responses.activate
def test_GithubCrawler_repo(keywords, proxies):
    responses.add(responses.GET, GitHubCrawler.BASE_URL + '/search?q=openstack+nova+css&type=Repositories',
                  body=repo_response, status=200)

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_urls(keywords, 'Repositories')
    assert result == expected_repo_urls


@responses.activate
def test_GithubCrawler_issues(keywords, proxies):
    responses.add(responses.GET, re.compile(GitHubCrawler.BASE_URL + '.*'), body=issues_response, status=200)

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_urls(keywords, 'Issues')
    assert result == expected_issues_urls


@responses.activate
def test_GithubCrawler_wikis(keywords, proxies):
    responses.add(responses.GET, re.compile(GitHubCrawler.BASE_URL + '.*'), body=wikis_response, status=200)

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_urls(keywords, 'Wikis')
    assert result == expected_wikis_urls
