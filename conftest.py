import logging

import requests
import pytest
from helper.browser_manager import BrowserManager
from helper.configuration_manager import ConfigurationManager

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def driver():
    driver = BrowserManager.initialize()
    yield driver
    BrowserManager.close()

@pytest.fixture(scope="session")
def web_app(driver, user: str = ConfigurationManager.username()):
    driver.get(ConfigurationManager.app_url() + "?user-id=" + user )
    yield driver

def _log_response(response, *args, **kwargs):
    req = response.request
    logger.info("%s %s → %s", req.method, req.url, response.status_code)

@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.headers.update({"x-user-id": ConfigurationManager.username()})
    session.hooks["response"].append(_log_response)
    yield session
    session.close()