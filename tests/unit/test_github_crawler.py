import re

import pytest
import responses

from github_crawler import GitHubCrawler
from tests.html_response import repo_response, issues_response, wikis_response


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
    assert result == [
        {
            "url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage"
        },
        {
            "url": "https://github.com/michealbalogun/Horizon-dashboard"
        }
    ]


@responses.activate
def test_GithubCrawler_issues(keywords, proxies):
    responses.add(responses.GET, re.compile(GitHubCrawler.BASE_URL + '.*'), body=issues_response, status=200)

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_urls(keywords, 'issues')
    assert result == [
        {
            "url": "https://github.com/sfPPP/openstack-note/issues/8"
        },
        {
            "url": "https://github.com/moby/moby/issues/19758"
        }
    ]


@responses.activate
def test_GithubCrawler_wikis(keywords, proxies):
    responses.add(responses.GET, re.compile(GitHubCrawler.BASE_URL + '.*'), body=wikis_response, status=200)

    crawler = GitHubCrawler(proxies)
    result = crawler.fetch_urls(keywords, 'wikis')
    assert result == [
        {
            "url": "https://github.com/vault-team/vault-website/wiki/Quick-installation-guide"
        },
        {
            "url": "https://github.com/marcosaletta/Juno-CentOS7-Guide/wiki/2.-Controller-and-Network-Node-Installation"
        }
    ]