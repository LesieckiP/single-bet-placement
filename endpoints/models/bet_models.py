from enum import StrEnum

from pydantic import BaseModel, Field

from helper.configuration_manager import ConfigurationManager


class Selection(StrEnum):
    HOME = "HOME"
    DRAW = "DRAW"
    AWAY = "AWAY"


class PlaceBetRequest(BaseModel):
    matchId: str
    selection: Selection
    stake: float = Field(ge=ConfigurationManager.min_stake(), le=ConfigurationManager.max_stake())


class PlaceBetResponse(BaseModel):
    message: str
    matchId: str
    selection: str
    stake: float
    odds: float
    payout: float
    balance: float
    currency: str
