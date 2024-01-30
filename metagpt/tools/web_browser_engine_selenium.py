#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

import asyncio
import importlib
from concurrent import futures
from copy import deepcopy
from typing import Literal

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.core.download_manager import WDMDownloadManager
from webdriver_manager.core.http import WDMHttpClient

from metagpt.config2 import config
from metagpt.utils.parse_html import WebPage


class SeleniumWrapper:
    """Wrapper around Selenium.

    To use this module, you should check the following:

    1. Run the following command: pip install metagpt[selenium].
    2. Make sure you have a compatible web browser installed and the appropriate WebDriver set up
       for that browser before running. For example, if you have Mozilla Firefox installed on your
       computer, you can set the configuration SELENIUM_BROWSER_TYPE to firefox. After that, you
       can scrape web pages using the Selenium WebBrowserEngine.

    Args:
        browser_type: Type of the browser to use. Defaults to 'chrome'.
        launch_kwargs: Additional arguments for launching the browser. Defaults to None.
        loop: Event loop to run asynchronous tasks. Defaults to None.
        executor: Executor for running synchronous functions asynchronously. Defaults to None.
    """

    def __init__(
        self,
        browser_type: Literal["chrome", "firefox", "edge", "ie"] = "chrome",
        launch_kwargs: dict | None = None,
        *,
        loop: asyncio.AbstractEventLoop | None = None,
        executor: futures.Executor | None = None,
    ) -> None:
        self.browser_type = browser_type
        launch_kwargs = launch_kwargs or {}
        if config.proxy and "proxy-server" not in launch_kwargs:
            launch_kwargs["proxy-server"] = config.proxy

        self.executable_path = launch_kwargs.pop("executable_path", None)
        self.launch_args = [f"--{k}={v}" for k, v in launch_kwargs.items()]
        self._has_run_precheck = False
        self._get_driver = None
        self.loop = loop
        self.executor = executor

    async def run(self, url: str, *urls: str) -> WebPage | list[WebPage]:
        """Runs the Selenium scraper on the given URL or URLs.

        Args:
            url: The primary URL to scrape.
            *urls: Additional URLs to scrape in parallel.

        Returns:
            A WebPage object if a single URL is provided, or a list of WebPage objects if multiple URLs are provided.
        """
        await self._run_precheck()

        _scrape = lambda url: self.loop.run_in_executor(self.executor, self._scrape_website, url)

        if urls:
            return await asyncio.gather(_scrape(url), *(_scrape(i) for i in urls))
        return await _scrape(url)

    async def _run_precheck(self):
        """Performs pre-checks and setups before running the scraper."""
        if self._has_run_precheck:
            return
        self.loop = self.loop or asyncio.get_event_loop()
        self._get_driver = await self.loop.run_in_executor(
            self.executor,
            lambda: _gen_get_driver_func(self.browser_type, *self.launch_args, executable_path=self.executable_path),
        )
        self._has_run_precheck = True

    def _scrape_website(self, url):
        """Scrapes the website at the given URL.

        Args:
            url: The URL of the website to scrape.

        Returns:
            A WebPage object containing the scraped page content and HTML.
        """
        with self._get_driver() as driver:
            try:
                driver.get(url)
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                inner_text = driver.execute_script("return document.body.innerText;")
                html = driver.page_source
            except Exception as e:
                inner_text = f"Fail to load page content for {e}"
                html = ""
            return WebPage(inner_text=inner_text, html=html, url=url)


_webdriver_manager_types = {
    "chrome": ("webdriver_manager.chrome", "ChromeDriverManager"),
    "firefox": ("webdriver_manager.firefox", "GeckoDriverManager"),
    "edge": ("webdriver_manager.microsoft", "EdgeChromiumDriverManager"),
    "ie": ("webdriver_manager.microsoft", "IEDriverManager"),
}


class WDMHttpProxyClient(WDMHttpClient):
    """HTTP client for WebDriver Manager with proxy support."""

    def get(self, url, **kwargs):
        """Sends a GET request.

        Args:
            url: URL for the GET request.
            **kwargs: Optional arguments that request takes.

        Returns:
            Response object.
        """
        if "proxies" not in kwargs and config.proxy:
            kwargs["proxies"] = {"all_proxy": config.proxy}
        return super().get(url, **kwargs)


def _gen_get_driver_func(browser_type, *args, executable_path=None):
    WebDriver = getattr(importlib.import_module(f"selenium.webdriver.{browser_type}.webdriver"), "WebDriver")
    Service = getattr(importlib.import_module(f"selenium.webdriver.{browser_type}.service"), "Service")
    Options = getattr(importlib.import_module(f"selenium.webdriver.{browser_type}.options"), "Options")

    if not executable_path:
        module_name, type_name = _webdriver_manager_types[browser_type]
        DriverManager = getattr(importlib.import_module(module_name), type_name)
        driver_manager = DriverManager(download_manager=WDMDownloadManager(http_client=WDMHttpProxyClient()))
        # driver_manager.driver_cache.find_driver(driver_manager.driver))
        executable_path = driver_manager.install()

    def _get_driver():
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--enable-javascript")
        if browser_type == "chrome":
            options.add_argument("--disable-gpu")  # This flag can help avoid renderer issue
            options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
            options.add_argument("--no-sandbox")
        for i in args:
            options.add_argument(i)
        return WebDriver(options=deepcopy(options), service=Service(executable_path=executable_path))

    return _get_driver
