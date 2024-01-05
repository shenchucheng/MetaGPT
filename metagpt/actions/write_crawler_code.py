#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/9/23 1:43
@Author  : shenchucheng
@File    : write_crawler_code.py
"""

from metagpt.actions.action import Action
from metagpt.schema import Message
from metagpt.tools.web_browser_engine import WebBrowserEngine
from metagpt.utils.common import CodeParser

PROMPT_TEMPLATE = """Please complete the web page crawler parse function to achieve the User Requirement. The parse \
function should take a BeautifulSoup object as input, which corresponds to the HTML outline provided in the Context.

```python
from bs4 import BeautifulSoup

# only complete the parse function
def parse(soup: BeautifulSoup):
    ...
    # Return the object that the user wants to retrieve, don't use print
```

## User Requirement
{requirement}

## Context

The outline of html page to scrabe is show like below:

```tree
{outline}
```
"""


class WriteCrawlerCode(Action):
    async def run(self, requirement):
        requirement: Message = requirement[-1]
        data = requirement.instruct_content.model_dump()
        urls = data["Crawler URL List"]
        query = data["Page Content Extraction"]

        codes = {}
        for url in urls:
            codes[url] = await self._write_code(url, query)
        return "\n".join(f"# {url}\n{code}" for url, code in codes.items())

    async def _write_code(self, url, query):
        page = await WebBrowserEngine().run(url)
        outline = page.get_outline()
        outline = "\n".join(
            f"{' '*i['depth']}{'.'.join([i['name'], *i.get('class', [])])}: {i['text'] if i['text'] else ''}"
            for i in outline
        )
        code_rsp = await self._aask(PROMPT_TEMPLATE.format(outline=outline, requirement=query))
        code = CodeParser.parse_code(block="", text=code_rsp)
        return code
