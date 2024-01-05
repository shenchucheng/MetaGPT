#!/usr/bin/env python
from __future__ import annotations

from typing import Generator, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from pydantic import BaseModel, PrivateAttr


class WebPage(BaseModel):
    inner_text: str
    html: str
    url: str

    _soup: Optional[BeautifulSoup] = PrivateAttr(default=None)
    _title: Optional[str] = PrivateAttr(default=None)

    @property
    def soup(self) -> BeautifulSoup:
        if self._soup is None:
            self._soup = BeautifulSoup(self.html, "html.parser")
        return self._soup

    @property
    def title(self):
        if self._title is None:
            title_tag = self.soup.find("title")
            self._title = title_tag.text.strip() if title_tag is not None else ""
        return self._title

    def get_links(self) -> Generator[str, None, None]:
        for i in self.soup.find_all("a", href=True):
            url = i["href"]
            result = urlparse(url)
            if not result.scheme and result.path:
                yield urljoin(self.url, url)
            elif url.startswith(("http://", "https://")):
                yield urljoin(self.url, url)

    def get_slim_soup(self, keep_links: bool = False):
        soup = _get_soup(self.html)
        if keep_links:
            return soup

        for i in soup.find_all(True):
            for name in list(i.attrs):
                if i[name] and name not in ["class"]:
                    del i[name]

        for i in soup.find_all(["svg", "img", "video", "audio"]):
            i.decompose()

        return soup

    def get_outline(self):
        soup = _get_soup(self.html)
        outline = []

        def process_element(element, depth):
            name = element.name
            if not name:
                return
            if name in ["script", "style"]:
                return

            element_info = {"name": element.name, "depth": depth}

            if name in ["svg"]:
                element_info["text"] = None
                outline.append(element_info)
                return

            element_info["text"] = element.string
            # Check if the element has an "id" attribute
            if "id" in element.attrs:
                element_info["id"] = element["id"]

            if "class" in element.attrs:
                element_info["class"] = element["class"]
            outline.append(element_info)
            for child in element.children:
                process_element(child, depth + 1)

        for element in soup.body.children:
            process_element(element, 1)

        return outline


def get_html_content(page: str, base: str):
    soup = _get_soup(page)

    return soup.get_text(strip=True)


def _get_soup(page: str):
    soup = BeautifulSoup(page, "html.parser")
    # https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
    for s in soup(["style", "script", "[document]", "head", "title", "footer"]):
        s.extract()

    return soup
