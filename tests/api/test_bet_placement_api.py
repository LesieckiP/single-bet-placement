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

    @pytest.mark.tc("BUG-01")
    def test_negative_stake_is_rejected(self):
        """Verify that placing a bet with a negative stake is rejected by the API"""
        match_id = self.bet_endpoint.get_matches()[0].id
        response = self.bet_endpoint.post("place-bet", json={
            "matchId": match_id,
            "selection": "HOME",
            "stake": -1
        })
        assert response.status_code >= 400, (
            f"Negative stake should be rejected but got {response.status_code}"
        )

    @pytest.mark.tc("BUG-02")
    def test_bet_rejected_when_balance_below_zero(self):
        """Verify that placing a bet is rejected when balance is below zero"""
        match_id = self.bet_endpoint.get_matches()[0].id
        balance = self.bet_endpoint.get_balance().balance

        # Drain balance to zero by betting the full amount
        self.bet_endpoint.post("place-bet", json={
            "matchId": match_id,
            "selection": "HOME",
            "stake": balance
        })

        response = self.bet_endpoint.post("place-bet", json={
            "matchId": match_id,
            "selection": "HOME",
            "stake": 1
        })
        assert response.status_code >= 400, (
            f"Bet with zero balance should be rejected but got {response.status_code}"
        )
