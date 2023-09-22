#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/9/23 1:43
@Author  : shenchucheng
@File    : crawling_engineer.py
"""

import asyncio
import sys
from uuid import uuid4

import aiofiles
import fire

from metagpt.actions.action import Action
from metagpt.const import WORKSPACE_ROOT
from metagpt.tools.web_browser_engine import WebBrowserEngine
from metagpt.utils.common import CodeParser

SYSTEM_PROMPT = """You are a professional web crawler engineer, using Playwright to retrieve web pages and bs4 to parse HTML with Python.
Note to return only in one code form, your code will be part of the entire project, so please implement complete, reliable, reusable code snippets.

```python
...
```
"""

PROMPT_TEMPLATE = """
## Requirement
{requirement}

## Context

The html of page to scrabe is show like below:

```html
{html}
```
"""


class WriteCrawlerCode(Action):
    async def run(self, url, query):
        page = await WebBrowserEngine().run(url)
        soup = page.get_slim_soup()
        code_rsp = await self._aask(PROMPT_TEMPLATE.format(html=soup, requirement=query), [SYSTEM_PROMPT])
        code = CodeParser.parse_code(block="", text=code_rsp)
        return code


async def main(url: str, query: str, run_code: bool = True):
    code = await WriteCrawlerCode().run(url, query)
    uid = uuid4().hex
    path = WORKSPACE_ROOT / "cawler" / uid / "cawler.py"
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(path, "w") as f:
        await f.write(code)

    if run_code and input(f"{code}\n Should the code be executed? Y/N\n") == "Y":
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(path.absolute()),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        print(stdout.decode(), stderr.decode())
    print(path)


if __name__ == "__main__":
    fire.Fire(main)
