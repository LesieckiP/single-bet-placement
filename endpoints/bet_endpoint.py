from endpoints.base_endpoint import BaseEndpoint
from endpoints.models.balance_models import BalanceResponse
from endpoints.models.bet_models import PlaceBetRequest, PlaceBetResponse
from endpoints.models.matches_models import MatchResponse


class BetEndpoint(BaseEndpoint):

    def get_matches(self) -> list[MatchResponse]:
        response = self.get("matches")
        self._raise_for_error(response)
        return [MatchResponse.model_validate(match) for match in response.json()]

    def get_balance(self) -> BalanceResponse:
        response = self.get("balance")
        self._raise_for_error(response)
        return BalanceResponse.model_validate(response.json())

    def reset_balance(self) -> BalanceResponse:
        response = self.post("reset-balance")
        self._raise_for_error(response)
        return BalanceResponse.model_validate(response.json())

    def place_bet(self, bet: PlaceBetRequest) -> PlaceBetResponse:
        response = self.post("place-bet", json=bet.model_dump())
        self._raise_for_error(response)
        return PlaceBetResponse.model_validate(response.json())