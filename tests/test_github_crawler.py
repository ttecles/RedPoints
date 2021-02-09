import re

import httpx
import pytest
import respx as respx

from crawlers import GitHubCrawler
from tests.html_response import repo_response, issues_response, wikis_response, expected_repo_urls, \
    expected_issues_urls, expected_wikis_urls, expected_repo_urls_extra, dropbox_cloud_storage_response, \
    horizon_dashboard_response, expected_horizon_data


@pytest.fixture
def keywords():
    return ["openstack", "nova", "css"]


@pytest.fixture
def proxies():
    return [
        "194.126.37.94:8080",
        "13.78.125.167:8080"
    ]


@respx.mock
def test_GithubCrawler_repo(keywords, proxies):
    respx.get(url=GitHubCrawler.BASE_URL + '/search?q=openstack+nova+css&type=Repositories').mock(
        return_value=httpx.Response(200, html=repo_response))

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_data(keywords, 'Repositories')
    assert result == expected_repo_urls


@respx.mock
def test_GithubCrawler_issues(keywords, proxies):
    respx.get(url=re.compile(GitHubCrawler.BASE_URL + '.*')).mock(
        return_value=httpx.Response(200, html=issues_response))

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_data(keywords, 'Issues')
    assert result == expected_issues_urls


@respx.mock
def test_GithubCrawler_wikis(keywords, proxies):
    respx.get(url=re.compile(GitHubCrawler.BASE_URL + '.*')).mock(
        return_value=httpx.Response(200, html=wikis_response))

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_data(keywords, 'Wikis')
    assert result == expected_wikis_urls


@respx.mock
def test_GithubCrawler_repo_extra(keywords, proxies):
    respx.get(url=GitHubCrawler.BASE_URL + '/search?q=openstack+nova+css&type=Repositories').mock(
        return_value=httpx.Response(200, html=repo_response))
    respx.get(url=GitHubCrawler.BASE_URL + '/atuldjadhav/DropBox-Cloud-Storage').mock(
        return_value=httpx.Response(200, html=dropbox_cloud_storage_response))
    respx.get(url=GitHubCrawler.BASE_URL + '/michealbalogun/Horizon-dashboard').mock(
        return_value=httpx.Response(200, html=horizon_dashboard_response))
    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_data(keywords, 'Repositories', extra=True)
    assert result == expected_repo_urls_extra


def test_GithubCrawler_invalid_type(keywords, proxies):
    crawler = GitHubCrawler(proxies)
    with pytest.raises(ValueError) as e:
        crawler.fetch_data(keywords, 'XXX')


@respx.mock
def test_GithubCrawler_repo_extra_error(keywords, proxies):
    respx.get(url=GitHubCrawler.BASE_URL + '/search?q=openstack+nova+css&type=Repositories').mock(
        return_value=httpx.Response(200, html=repo_response))
    respx.get(url=GitHubCrawler.BASE_URL + '/atuldjadhav/DropBox-Cloud-Storage').mock(
        return_value=httpx.Response(500, html=dropbox_cloud_storage_response))
    respx.get(url=GitHubCrawler.BASE_URL + '/michealbalogun/Horizon-dashboard').mock(
        return_value=httpx.Response(200, html=horizon_dashboard_response))
    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_data(keywords, 'Repositories', extra=True)
    assert result == [
        {
            "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
            "extra": None
        },
        {
            "url": "https://github.com/michealbalogun/Horizon-dashboard",
            "extra": {
                "owner": "michealbalogun",
                "language_stats": expected_horizon_data
            }
        }
    ]