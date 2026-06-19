import time

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from endpoints.bet_endpoint import BetEndpoint
from endpoints.models.matches_models import MatchResponse
from pages.bet_slip import BetSlipPage
from pages.main_page import MainPage
from pages.receipt_modal import ReceiptModal


@pytest.fixture(autouse=True, scope="class")
def setup_and_teardown(request, web_app, api_session):
    """Reset balance, place a bet on the first match, and capture receipt modal values."""
    bet_endpoint = BetEndpoint(api_session)
    request.cls.main_page = MainPage(web_app)
    request.cls.bet_slip_page = BetSlipPage(web_app)
    request.cls.receipt_modal = ReceiptModal(web_app)
    request.cls.bet_endpoint = bet_endpoint
    request.cls.driver = web_app

    bet_endpoint.reset_balance()
    request.cls.initial_balance = bet_endpoint.get_balance().balance

    # Get the first match from API for ground-truth comparison
    matches = bet_endpoint.get_matches()
    request.cls.match = matches[0]

    web_app.refresh()
    time.sleep(2)

    # Place a bet via UI
    stake = 5.0
    request.cls.stake = stake
    request.cls.expected_odds = matches[0].odds.home

    main_page = MainPage(web_app)
    bet_slip = BetSlipPage(web_app)
    main_page.click_first_possible_odds_button()
    time.sleep(1)
    bet_slip.input_bet_slip_stake(stake)
    time.sleep(1)
    bet_slip.get_place_bet_button().click()

    # Wait for receipt modal to appear
    receipt = ReceiptModal(web_app)
    receipt.is_displayed()
    time.sleep(1)

    # Capture all modal values before any test runs
    request.cls.receipt_match = receipt.get_match()
    request.cls.receipt_stake = receipt.get_stake()
    request.cls.receipt_odds = receipt.get_odds()
    request.cls.receipt_payout = receipt.get_payout()
    request.cls.receipt_bet_id = receipt.get_bet_id()

    yield

    bet_endpoint.reset_balance()


class TestSuccessReceipt:
    main_page: MainPage
    bet_slip_page: BetSlipPage
    receipt_modal: ReceiptModal
    bet_endpoint: BetEndpoint
    driver: WebDriver
    initial_balance: float
    match: MatchResponse
    stake: float
    expected_odds: float
    receipt_match: str
    receipt_stake: float
    receipt_odds: float
    receipt_payout: float
    receipt_bet_id: str

    @pytest.mark.tc("TC-09")
    def test_receipt_displays_correct_stake(self):
        """TC-09: Receipt stake matches the entered stake value"""
        assert self.receipt_stake == pytest.approx(self.stake, abs=0.01), (
            f"Receipt stake {self.receipt_stake} does not match entered stake {self.stake}"
        )

    @pytest.mark.tc("TC-09")
    def test_receipt_displays_correct_odds(self):
        """TC-09: Receipt odds match the selected outcome's odds from API"""
        assert self.receipt_odds == pytest.approx(self.expected_odds, abs=0.01), (
            f"Receipt odds {self.receipt_odds} does not match API odds {self.expected_odds}"
        )

    @pytest.mark.tc("TC-09")
    def test_receipt_has_bet_id(self):
        """TC-09: Receipt displays a non-empty bet ID"""
        assert self.receipt_bet_id, "Receipt bet ID is empty"

    @pytest.mark.xfail(reason="BUG-05: Payout in confirmation pop-up does not match stake × odds — appears to always double the stake value", strict=False)
    @pytest.mark.tc("TC-09")
    def test_receipt_payout_equals_stake_times_odds(self):
        """TC-09: Receipt payout equals stake × odds"""
        expected_payout = self.stake * self.expected_odds
        assert self.receipt_payout == pytest.approx(expected_payout, abs=0.01), (
            f"Receipt payout {self.receipt_payout} does not match stake × odds = {self.stake} × {self.expected_odds} = {expected_payout}"
        )

    @pytest.mark.xfail(reason="BUG-10: Home/Away team order in confirmation pop-up is swapped relative to the match list", strict=False)
    @pytest.mark.tc("TC-09")
    def test_receipt_match_name_matches_api_team_order(self):
        """TC-09: Receipt match name shows homeTeam vs awayTeam in correct order"""
        expected_match = f"{self.match.homeTeam} vs {self.match.awayTeam}"
        assert self.receipt_match == expected_match, (
            f"Receipt match '{self.receipt_match}' does not match expected '{expected_match}' (home vs away per API)"
        )
