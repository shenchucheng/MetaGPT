#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/1/11 17:25
# @Author  : alexanderwu
# @File    : context_mixin.py

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from metagpt.config2 import Config
from metagpt.context import Context
from metagpt.provider.base_llm import BaseLLM


class ContextMixin(BaseModel):
    """Mixin class for context and config.

    This class is designed to be a mixin for handling context, configuration, and language model (LLM) instances
    within a larger application structure. It provides methods to set and retrieve these components, ensuring
    that they are appropriately initialized and accessible throughout the application.

    Attributes:
        model_config: A dictionary allowing arbitrary types, intended for model configuration.
        private_context: An optional Context instance, not included in the model's serialization.
        private_config: An optional Config instance, not included in the model's serialization.
        private_llm: An optional BaseLLM instance, not included in the model's serialization.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Pydantic has bug on _private_attr when using inheritance, so we use private_* instead
    # - https://github.com/pydantic/pydantic/issues/7142
    # - https://github.com/pydantic/pydantic/issues/7083
    # - https://github.com/pydantic/pydantic/issues/7091

    # Env/Role/Action will use this context as private context, or use self.context as public context
    private_context: Optional[Context] = Field(default=None, exclude=True)
    # Env/Role/Action will use this config as private config, or use self.context.config as public config
    private_config: Optional[Config] = Field(default=None, exclude=True)

    # Env/Role/Action will use this llm as private llm, or use self.context._llm instance
    private_llm: Optional[BaseLLM] = Field(default=None, exclude=True)

    def __init__(
        self,
        context: Optional[Context] = None,
        config: Optional[Config] = None,
        llm: Optional[BaseLLM] = None,
        **kwargs,
    ):
        """Initialize the mixin with optional context, config, and llm instances.

        Args:
            context: An optional Context instance to initialize with.
            config: An optional Config instance to initialize with.
            llm: An optional BaseLLM instance to initialize with.
        """
        super().__init__(**kwargs)
        self.set_context(context)
        self.set_config(config)
        self.set_llm(llm)

    def set(self, k, v, override=False):
        """Set an attribute on the instance.

        Args:
            k: The attribute name to set.
            v: The value to set the attribute to.
            override: If True, the attribute will be set even if it already exists.
        """
        if override or not self.__dict__.get(k):
            self.__dict__[k] = v

    def set_context(self, context: Context, override=True):
        """Set the context attribute.

        Args:
            context: The Context instance to set.
            override: If True, the context will be set even if it already exists.
        """
        self.set("private_context", context, override)

    def set_config(self, config: Config, override=False):
        """Set the config attribute.

        Args:
            config: The Config instance to set.
            override: If True, the config will be set even if it already exists.
        """
        self.set("private_config", config, override)
        if config is not None:
            _ = self.llm  # init llm

    def set_llm(self, llm: BaseLLM, override=False):
        """Set the llm (language model) attribute.

        Args:
            llm: The BaseLLM instance to set.
            override: If True, the llm will be set even if it already exists.
        """
        self.set("private_llm", llm, override)

    @property
    def config(self) -> Config:
        """Set the config instance.

        Args:
            config: The Config instance to set.
        """
        if self.private_config:
            return self.private_config
        return self.context.config

    @config.setter
    def config(self, config: Config) -> None:
        """Set the config instance.

        Args:
            config: The Config instance to set.
        """
        self.set_config(config)

    @property
    def context(self) -> Context:
        """Set the context instance.

        Args:
            context: The Context instance to set.
        """
        if self.private_context:
            return self.private_context
        return Context()

    @context.setter
    def context(self, context: Context) -> None:
        """Set the context instance.

        Args:
            context: The Context instance to set.
        """
        self.set_context(context)

    @property
    def llm(self) -> BaseLLM:
        """Set the language model (LLM) instance.

        Args:
            llm: The BaseLLM instance to set.
        """
        # print(f"class:{self.__class__.__name__}({self.name}), llm: {self._llm}, llm_config: {self._llm_config}")
        if not self.private_llm:
            self.private_llm = self.context.llm_with_cost_manager_from_llm_config(self.config.llm)
        return self.private_llm

    @llm.setter
    def llm(self, llm: BaseLLM) -> None:
        """Set the language model (LLM) instance.

        Args:
            llm: The BaseLLM instance to set.
        """
        self.private_llm = llm
