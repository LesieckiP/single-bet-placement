import pytest
import requests

from helper.browser_manager import BrowserManager
from helper.configuration_manager import ConfigurationManager


@pytest.fixture(scope="session")
def driver():
    driver = BrowserManager.initialize()
    yield driver
    BrowserManager.close()

@pytest.fixture(scope="session")
def web_app(driver, user: str = ConfigurationManager.username()):
    driver.get(ConfigurationManager.app_url() + "?user-id=" + user )
    yield driver

@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update({"x-user-id": ConfigurationManager.username()})
    yield session
    session.close()