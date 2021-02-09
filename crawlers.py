import asyncio
import random
import typing as t
from urllib.parse import urlencode

import httpx as httpx
from lxml import html as html_parser


class GitHubCrawler:
    BASE_URL = "https://github.com"
    TYPES = {'Repositories': '//ul[@class="repo-list"]//a[@data-hydro-click]',
             'Issues': '//div[@class="issue-list"]//a[@data-hydro-click]',
             'Wikis': '//*[@id="wiki_search_results"]//a[@data-hydro-click]'}

    def __init__(self, proxies: t.List[str], timeout: t.Union[int, float] = None):
        """ Searches for the keywords using one of the proxies and collects all URLs based on type_

        :param proxies: list of proxies to use on fetching data
        :param timeout: timeout used for fetching data
        """
        self._proxies = proxies
        self.timeout = timeout

    def fetch_data(self, keywords: t.List[str], type_: str, extra=False):
        if type_ not in self.TYPES:
            raise ValueError("Not a valid type")
        proxies = random.choice(self._proxies) if self._proxies else None
        if proxies:
            proxies = {f'http://{proxies}': None}

        resp = httpx.get(self.BASE_URL + '/search', params=dict(q=' '.join(keywords), type=type_),
                         proxies=proxies, timeout=self.timeout)
        if resp.status_code == 200:
            return self._extract_data(resp.content, type_, extra)

    def _parse(self, html, xpath) -> t.Iterator[str]:
        tree = html_parser.fromstring(html)
        elements = tree.xpath(xpath)
        return [self.BASE_URL + e.get('href') for e in elements if e.get('href')]

    def _extract_data(self, html, type_, extra):
        urls = self._parse(html, self.TYPES[type_])
        if type_ == 'Repositories' and extra:
            extra = asyncio.run(self._async_get_extra_data(urls))
            data = [dict(url=url, extra=extra.get(url)) for url in urls]
        else:
            data = [dict(url=url) for url in urls]
        return data

    async def _async_get_extra_data(self, urls):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [client.get(url) for url in urls]
            responses = await asyncio.gather(*tasks, return_exceptions=False)
        fetched = {}
        for resp in responses:

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
                        aux = [span.text for span in li.xpath('.//span')][-2:]
                        if aux:
                            language_stats.update({aux[0]: float(aux[1].strip('%'))})
                    except (ValueError, IndexError):
                        pass
                fetched.update({resp.url: dict(owner=owner, language_stats=language_stats)})
        return fetched
