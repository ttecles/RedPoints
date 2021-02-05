import random
import re
import typing as t
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup


class GitHubCrawler:
    BASE_URL = "https://github.com"

    def __init__(self, proxies: t.List[str], timeout: t.Union[int, float] = None):
        """ Searches for the keywords using one of the proxies and collects all URLs based on type

        :param proxies: list of proxies to use on fetching data
        :param timeout: timeout used for fetching data
        """
        self._proxies = proxies
        self.timeout = timeout

    def fetch_urls(self, keywords: t.List[str], type: str):
        proxy = random.choice(self._proxies)

        if self._proxies:
            proxies = {'http': f'http://{proxy}'}
        else:
            proxies = None

        req = requests.get(self.BASE_URL + '/search?' + urlencode(dict(q=' '.join(keywords), type=type)),
                           proxies=proxies, timeout=self.timeout)
        if req.ok:
            soup = BeautifulSoup(req.content, 'html.parser')

            return self._extract_data(soup, type)

    def _extract_data(self, soup, type):
        if type == 'Wikis':
            data = self._parse_wikis(soup)
        elif type == 'Issues':
            data = self._parse_issues(soup)
        elif type == 'Repositories':
            data = self._parse_repo(soup)
        else:
            raise ValueError(f"type not supported: {type}")

        return data

    def _parse_repo(self, soup):
        elements = soup.find('ul', class_='repo-list').find_all('a', href=True,
                                                                attrs={'data-hydro-click': re.compile(".*")})
        return [{'url': self.BASE_URL + e.attrs['href']} for e in elements]

    def _parse_issues(self, soup):
        elements = soup.find('div', class_='issue-list').find_all('a', href=True,
                                                                  attrs={'data-hydro-click': re.compile(".*")})
        return [{'url': self.BASE_URL + e.attrs['href']} for e in elements]

    def _parse_wikis(self, soup):
        elements = soup.find(id='wiki_search_results').find_all('a', href=True,
                                                                attrs={'data-hydro-click': re.compile(".*")})
        return [{'url': self.BASE_URL + e.attrs['href']} for e in elements]
