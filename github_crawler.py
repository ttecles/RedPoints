import asyncio
import random
import re
import typing as t
from urllib.parse import urlencode

import httpx as httpx
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

    def fetch_urls(self, keywords: t.List[str], type: str, extra=False):
        proxy = random.choice(self._proxies)

        if self._proxies:
            proxies = {'http': f'http://{proxy}'}
        else:
            proxies = None

        req = requests.get(self.BASE_URL + '/search?' + urlencode(dict(q=' '.join(keywords), type=type)),
                           proxies=proxies, timeout=self.timeout)
        if req.ok:
            soup = BeautifulSoup(req.content, 'html.parser')

            return self._extract_data(soup, type, extra)

    def _extract_data(self, soup, type, extra):
        if type == 'Wikis':
            data = self._parse_wikis(soup)
        elif type == 'Issues':
            data = self._parse_issues(soup)
        elif type == 'Repositories':
            data = self._parse_repo(soup, extra)
        else:
            raise ValueError(f"type not supported: {type}")

        return data

    async def _async_get_extra_data(self, urls):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [client.get(url) for url in urls]
            responses = await asyncio.gather(*tasks, return_exceptions=False)
        data = []
        for resp in responses:
            fetched = {}
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, 'html.parser')
                owner = soup.find('a', rel='author').text
                language_stats = {}
                for li in soup.find('h2', text="Languages").parent('li'):
                    aux = [span.text for span in li('span')]
                    if aux:
                        language_stats.update({aux[0]: float(aux[1].strip('%'))})
                fetched.update(url=str(resp.url), extra=dict(owner=owner, language_stats=language_stats))
            else:
                fetched.update(url=str(resp.url))
            data.append(fetched)
        return data

    def _parse_repo(self, soup, extra):
        elements = soup.find('ul', class_='repo-list').find_all('a', href=True,
                                                                attrs={'data-hydro-click': re.compile(".*")})
        urls = iter(self.BASE_URL + e.attrs['href'] for e in elements)
        if extra:
            return asyncio.run(self._async_get_extra_data(urls))
        return [{'url': url} for url in urls]

    def _parse_issues(self, soup):
        elements = soup.find('div', class_='issue-list').find_all('a', href=True,
                                                                  attrs={'data-hydro-click': re.compile(".*")})
        return [{'url': self.BASE_URL + e.attrs['href']} for e in elements]

    def _parse_wikis(self, soup):
        elements = soup.find(id='wiki_search_results').find_all('a', href=True,
                                                                attrs={'data-hydro-click': re.compile(".*")})
        return [{'url': self.BASE_URL + e.attrs['href']} for e in elements]
