#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/9/26 14:27
# @Author  : zhanglei
# @File    : moderation.py

from typing import Union

from metagpt.provider.base_llm import BaseLLM


class Moderation:
    """Handles moderation tasks using a language model.

    This class provides methods to perform content moderation by utilizing a language model.

    Attributes:
        llm: An instance of BaseLLM used for moderation.
    """

    def __init__(self, llm: BaseLLM):
        """Initializes the Moderation class with a language model.

        Args:
            llm: An instance of BaseLLM.
        """
        self.llm = llm

    def handle_moderation_results(self, results):
        """Processes the raw moderation results to extract relevant information.

        Args:
            results: The raw results from the moderation model.

        Returns:
            A list of dictionaries with keys 'flagged' and 'true_categories' indicating
            whether the content was flagged and the categories it was flagged for.
        """
        resp = []
        for item in results:
            categories = item.categories.dict()
            true_categories = [category for category, item_flagged in categories.items() if item_flagged]
            resp.append({"flagged": item.flagged, "true_categories": true_categories})
        return resp

    async def amoderation_with_categories(self, content: Union[str, list[str]]):
        """Asynchronously moderates content and returns categories for which the content was flagged.

        Args:
            content: The content to be moderated, can be a string or a list of strings.

        Returns:
            A list of dictionaries with moderation results, including categories for flagged content.
        """
        resp = []
        if content:
            moderation_results = await self.llm.amoderation(content=content)
            resp = self.handle_moderation_results(moderation_results.results)
        return resp

    async def amoderation(self, content: Union[str, list[str]]):
        """Asynchronously moderates content and returns a simple flagged status.

        Args:
            content: The content to be moderated, can be a string or a list of strings.

        Returns:
            A list indicating whether each piece of content was flagged.
        """
        resp = []
        if content:
            moderation_results = await self.llm.amoderation(content=content)
            results = moderation_results.results
            for item in results:
                resp.append(item.flagged)

        return resp
