import logging

import pytest

from endpoints.bet_endpoint import BetEndpoint

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="class")
def setup_and_teardown(request, api_session):
    request.cls.bet_endpoint = BetEndpoint(api_session)

    yield

    BetEndpoint(api_session).reset_balance()


class TestBetPlacement:
    bet_endpoint: BetEndpoint
