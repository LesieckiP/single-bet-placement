import logging
import time

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from endpoints.bet_endpoint import BetEndpoint
from pages.bet_slip import BetSlipPage
from pages.main_page import MainPage

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True, scope="class")
def setup_and_teardown(request, web_app, api_session):
    """Reset balance for double-submit tests"""
    bet_endpoint = BetEndpoint(api_session)
    request.cls.main_page = MainPage(web_app)
    request.cls.bet_slip_page = BetSlipPage(web_app)
    request.cls.bet_endpoint = bet_endpoint
    request.cls.driver = web_app

    bet_endpoint.reset_balance()
    request.cls.initial_balance = bet_endpoint.get_balance().balance

    yield

    bet_endpoint.reset_balance()


class TestDoubleSubmit:
    main_page: MainPage
    bet_slip_page: BetSlipPage
    bet_endpoint: BetEndpoint
    driver: WebDriver
    initial_balance: float

    @pytest.mark.xfail(reason="Race condition: double-submit protection is inconsistent — rapid double-click sometimes creates two bets", strict=False)
    @pytest.mark.tc("TC-01")
    def test_double_click_place_bet_creates_single_bet(self):
        """TC-01: Verify rapid double-click on Place Bet creates only one bet and deducts stake once"""
        stake = 5.0
        assert self.main_page.get_title() == "Sports Betting QA", "Page not loaded correctly"

        balance_before = self.bet_endpoint.get_balance().balance

        self.main_page.click_first_possible_odds_button()
        self.bet_slip_page.input_bet_slip_stake(stake)
        assert self.bet_slip_page.get_place_bet_button().is_enabled(), "Place Bet button should be enabled"

        self.bet_slip_page.double_click_place_bet()

        time.sleep(3)

        balance_after = self.bet_endpoint.get_balance().balance
        deduction = balance_before - balance_after

        assert deduction == pytest.approx(stake, abs=0.01), (
            f"Expected single deduction of {stake}, but balance changed by {deduction} "
            f"(before: {balance_before}, after: {balance_after})"
        )
