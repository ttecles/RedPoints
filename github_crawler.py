import asyncio
import random
import typing as t
from urllib.parse import urlencode

import httpx as httpx
from lxml import html as html_parser


class GitHubCrawler:
    BASE_URL = "https://github.com"
    TYPES = ['Repositories', 'Issues', 'Wikis']

    def __init__(self, proxies: t.List[str], timeout: t.Union[int, float] = None):
        """ Searches for the keywords using one of the proxies and collects all URLs based on type

        :param proxies: list of proxies to use on fetching data
        :param timeout: timeout used for fetching data
        """
        self._proxies = proxies
        self.timeout = timeout

    def fetch_urls(self, keywords: t.List[str], type: str, extra=False):
        if type not in self.TYPES:
            raise ValueError("Not a valid type")
        proxies = random.choice(self._proxies) if self._proxies else None
        if proxies:
            proxies = {'http': f'http://{proxies}'}

        resp = httpx.get(self.BASE_URL + '/search?' + urlencode(dict(q=' '.join(keywords), type=type)),
                         proxies=proxies, timeout=self.timeout)
        if resp.status_code == 200:
            return self._extract_data(resp.content, type, extra)

    def _extract_data(self, html, type, extra):
        data = []
        if type == 'Wikis':
            data = self._parse_wikis(html)
        elif type == 'Issues':
            data = self._parse_issues(html)
        elif type == 'Repositories':
            data = self._parse_repo(html, extra)

        return data

    async def _async_get_extra_data(self, urls):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [client.get(url) for url in urls]
            responses = await asyncio.gather(*tasks, return_exceptions=False)
        data = []
        for resp in responses:
            fetched = {}
            if resp.status_code == 200:
                tree = html_parser.fromstring(resp.content)
                e = tree.xpath('//a[@rel="author"]')
                if e:
                    owner = e[0].text
                else:
                    owner = None
                language_stats = {}
                for li in tree.xpath('//h2[text()="Languages"]/..//li'):
                    try:
                        aux = [span.text for span in li.cssselect('span')][-2:]
                        if aux:
                            language_stats.update({aux[0]: float(aux[1].strip('%'))})
                    except:
                        pass
                fetched.update(url=str(resp.url), extra=dict(owner=owner, language_stats=language_stats))
            else:
                fetched.update(url=str(resp.url))
            data.append(fetched)
        return data

    def _parse_repo(self, html, extra):
        tree = html_parser.fromstring(html)
        elements = tree.xpath('//ul[@class="repo-list"]//a[@data-hydro-click]')
        urls = iter(self.BASE_URL + e.get('href', None) for e in elements if e.get('href', None))
        if extra:
            return asyncio.run(self._async_get_extra_data(urls))
        return [{'url': url} for url in urls]

    def _parse_issues(self, html):
        tree = html_parser.fromstring(html)
        elements = tree.xpath('//div[@class="issue-list"]//a[@data-hydro-click]')
        return [{'url': self.BASE_URL + e.get('href', None)} for e in elements if e.get('href', None)]

    def _parse_wikis(self, html):
        tree = html_parser.fromstring(html)
        elements = tree.xpath('//*[@id="wiki_search_results"]//a[@data-hydro-click]')
        return [{'url': self.BASE_URL + e.get('href', None)} for e in elements if e.get('href', None)]
