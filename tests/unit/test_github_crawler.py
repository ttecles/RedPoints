import re

import httpx
import pytest
import responses
import respx as respx

from github_crawler import GitHubCrawler
from tests.html_response import repo_response, issues_response, wikis_response, expected_repo_urls, \
    expected_issues_urls, expected_wikis_urls, expected_repo_urls_extra, dropbox_cloud_storage_response, \
    horizon_dashboard_response


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


@responses.activate
@respx.mock
def test_GithubCrawler_repo_extra(keywords, proxies):
    responses.add(responses.GET, GitHubCrawler.BASE_URL + '/search?q=openstack+nova+css&type=Repositories',
                  body=repo_response)
    respx.get(url=GitHubCrawler.BASE_URL + '/atuldjadhav/DropBox-Cloud-Storage').mock(
        return_value=httpx.Response(200, html=dropbox_cloud_storage_response))
    respx.get(url=GitHubCrawler.BASE_URL + '/michealbalogun/Horizon-dashboard').mock(
        return_value=httpx.Response(200, html=horizon_dashboard_response))
    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_urls(keywords, 'Repositories', extra=True)
    assert result == expected_repo_urls_extra
