#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/9/23 1:43
@Author  : shenchucheng
@File    : crawling_engineer.py
"""


from metagpt.actions.parse_sub_requirement import ParseSubRequirement
from metagpt.actions.write_crawler_code import WriteCrawlerCode
from metagpt.roles import Role


class CrawlerEngineer(Role):
    name: str = "John"
    profile: str = "Crawling Engineer"
    goal: str = "Write elegant, readable, extensible, efficient code"
    constraints: str = "The code should conform to standards like PEP8 and be modular and maintainable"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self._init_actions([WriteCrawlerCode])
        self._watch([ParseSubRequirement])
