from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

from helper.configuration_manager import ConfigurationManager

_DRIVER: WebDriver | None = None


class BrowserManager:
    @staticmethod
    def initialize() -> WebDriver:
        global _DRIVER
        if _DRIVER is not None:
            return _DRIVER

        browser = ConfigurationManager.browser()

        if browser == "chromium":
            _DRIVER = webdriver.Chrome()
        elif browser == "firefox":
            _DRIVER = webdriver.Firefox()
        else:
            raise ValueError(f"Unsupported Browser: {browser}")

        return _DRIVER

    @staticmethod
    def close():
        global _DRIVER
        if _DRIVER is not None:
            _DRIVER.quit()
            _DRIVER = None