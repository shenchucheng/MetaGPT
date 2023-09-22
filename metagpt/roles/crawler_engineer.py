#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2023/9/23 1:43
@Author  : shenchucheng
@File    : crawling_engineer.py
"""
import time

import aiofiles

from metagpt.actions import WriteCrawlerCode, WriteCrawlerPRD
from metagpt.actions.add_requirement import BossRequirement
from metagpt.const import WORKSPACE_ROOT
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message


class CrawlerEngineer(Role):
    def __init__(
        self,
        name: str = "John",
        profile: str = "Crawling Engineer",
        goal: str = "Write elegant, readable, extensible, efficient code",
        constraints: str = "The code should conform to standards like PEP8 and be modular and maintainable",
    ) -> None:
        """Initializes the Engineer role with given attributes."""
        super().__init__(name, profile, goal, constraints)
        self._init_actions([WriteCrawlerCode])
        self._watch([WriteCrawlerPRD])

    async def _act(self) -> Message:
        context = self._rc.important_memory
        prd = context[-1].instruct_content.dict()
        url = prd["Target Website Url"].strip('\n"')
        query = None
        if self._rc.env:
            requirement = self._rc.env.memory.get_by_action(BossRequirement)
            if requirement:
                query = requirement[-1].content
        query = query or prd["Original Requirements"]
        code = await self._rc.todo.run(url, query)
        await self._save_project(prd, code)
        msg = Message(content=code, role=self.profile, cause_by=type(self._rc.todo))
        self._rc.memory.add(msg)
        return msg

    async def _save_project(self, prd, code):
        package_name = prd["Python package name"].strip('\n"')
        root = WORKSPACE_ROOT / package_name
        if root.exists():
            root = WORKSPACE_ROOT / f"{package_name}_{time.strftime('%Y%m%d%H%M%S')}"
        root.mkdir(exist_ok=True, parents=True)
        path = root / f"{package_name}.py"
        async with aiofiles.open(root / "prd.md", "w") as f:
            content = "\n\n".join(f"## {k}\n{v}" for k, v in prd.items())
            await f.write(content)

        async with aiofiles.open(path, "w") as f:
            await f.write(code)
        logger.info(f"Done {root} generating.")
