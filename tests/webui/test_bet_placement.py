import logging

import pytest

from endpoints.bet_endpoint import BetEndpoint
from endpoints.models.bet_models import PlaceBetRequest, Selection
from pages.bet_slip import BetSlipPage
from pages.main_page import MainPage

@pytest.fixture(autouse=True, scope="class")
def setup_and_teardown(request, web_app, api_session):
    """Setup for the test - ensure balance is within bet boundary"""
    bet_endpoint = BetEndpoint(api_session)
    request.cls.main_page = MainPage(web_app)
    request.cls.bet_slip_page = BetSlipPage(web_app)

    request.cls.target = 40
    bet_endpoint.reset_balance()
    request.cls.balance = bet_endpoint.get_balance().balance

    match_id = bet_endpoint.get_matches()[0].id
    excess = request.cls.balance - request.cls.target
    bet_endpoint.place_bet(PlaceBetRequest(matchId=match_id, selection=Selection.HOME, stake=excess))
    request.cls.balance = bet_endpoint.get_balance().balance

    yield

    # bet_endpoint.reset_balance()

class TestBetPlacement:
    main_page: MainPage
    bet_slip_page: BetSlipPage
    target: float

    @pytest.mark.tc("TC-03")
    def test_stake_exceeding_balance(self):
        """Verify that user cannot place a bet that exceeds his balance"""
        assert self.main_page.get_title() == "Sports Betting QA", "Page not opened correctly"
        # assert self.main_page.get_balance() >= ConfigurationManager.max_stake(), "Balance between api and website does not match"
        self.main_page.click_first_possible_odds_button()
        self.bet_slip_page.input_bet_slip_stake(self.target + 1)
        assert "Insufficient balance" in self.bet_slip_page.get_validation_message(), "Insufficient balance error not shown"
        assert not self.bet_slip_page.get_place_bet_button().is_enabled(), "Place button was enabled but shouldn't!"

    @pytest.mark.tc("TC-02")
    def test_successful_bet_placement(self):
        """Verify that user can place a bet within his balance and it's deducted properly"""
        assert self.main_page.get_title() == "Sports Betting QA", "Page not opened correctly"
        self.main_page.click_first_possible_odds_button()
        self.bet_slip_page.input_bet_slip_stake(self.target - 1)
        assert self.bet_slip_page.get_place_bet_button().is_enabled(), "Place button should be enabled"
        self.bet_slip_page.get_place_bet_button().click()
        assert self.main_page.get_balance() < self.target, "Balance was not reduced after placing bet"