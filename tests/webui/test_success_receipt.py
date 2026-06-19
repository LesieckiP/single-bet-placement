import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from endpoints.bet_endpoint import BetEndpoint
from endpoints.models.matches_models import MatchResponse
from pages.bet_slip import BetSlipPage
from pages.main_page import MainPage
from pages.receipt_modal import ReceiptModal

STAKE = 5.0


@pytest.fixture(autouse=True, scope="class")
def setup_and_teardown(request, web_app, api_session):
    """Reset balance and initialize page objects for receipt tests."""
    bet_endpoint = BetEndpoint(api_session)
    request.cls.main_page = MainPage(web_app)
    request.cls.bet_slip_page = BetSlipPage(web_app)
    request.cls.receipt_modal = ReceiptModal(web_app)
    request.cls.bet_endpoint = bet_endpoint
    request.cls.driver = web_app

    bet_endpoint.reset_balance()
    request.cls.initial_balance = bet_endpoint.get_balance().balance
    request.cls.match = bet_endpoint.get_matches()[0]

    web_app.refresh()

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

    def _place_bet_and_read_receipt(self):
        """Place a bet on the first match and return receipt values. Cached after first call."""
        if hasattr(self, "_receipt"):
            return self._receipt

        self.main_page.click_first_possible_odds_button()
        self.bet_slip_page.input_bet_slip_stake(STAKE)
        self.bet_slip_page.get_place_bet_button().click()
        self.receipt_modal.is_displayed()

        self._receipt = {
            "match": self.receipt_modal.get_match(),
            "stake": self.receipt_modal.get_stake(),
            "odds": self.receipt_modal.get_odds(),
            "payout": self.receipt_modal.get_payout(),
            "bet_id": self.receipt_modal.get_bet_id(),
        }
        return self._receipt

    @pytest.mark.tc("TC-09")
    def test_receipt_displays_correct_stake_odds_and_bet_id(self):
        """TC-09: Receipt displays correct stake, odds, and a non-empty bet ID"""
        receipt = self._place_bet_and_read_receipt()
        expected_odds = self.match.odds.home

        assert receipt["stake"] == pytest.approx(STAKE, abs=0.01), (
            f"Receipt stake {receipt['stake']} does not match entered stake {STAKE}"
        )
        assert receipt["odds"] == pytest.approx(expected_odds, abs=0.01), (
            f"Receipt odds {receipt['odds']} does not match API odds {expected_odds}"
        )
        assert receipt["bet_id"], "Receipt bet ID is empty"

    @pytest.mark.xfail(reason="BUG-05: Payout in confirmation pop-up does not match stake × odds — appears to always double the stake value", strict=False)
    @pytest.mark.tc("TC-09")
    def test_receipt_payout_equals_stake_times_odds(self):
        """TC-09: Receipt payout equals stake × odds"""
        receipt = self._place_bet_and_read_receipt()
        expected_payout = STAKE * self.match.odds.home

        assert receipt["payout"] == pytest.approx(expected_payout, abs=0.01), (
            f"Receipt payout {receipt['payout']} does not match stake × odds = {STAKE} × {self.match.odds.home} = {expected_payout}"
        )

    @pytest.mark.xfail(reason="BUG-10: Home/Away team order in confirmation pop-up is swapped relative to the match list", strict=False)
    @pytest.mark.tc("TC-09")
    def test_receipt_match_name_matches_api_team_order(self):
        """TC-09: Receipt match name shows homeTeam vs awayTeam in correct order"""
        receipt = self._place_bet_and_read_receipt()
        expected_match = f"{self.match.homeTeam} vs {self.match.awayTeam}"

        assert receipt["match"] == expected_match, (
            f"Receipt match '{receipt['match']}' does not match expected '{expected_match}' (home vs away per API)"
        )
