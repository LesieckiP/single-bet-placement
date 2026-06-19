from datetime import date

from pydantic import BaseModel


class Odds(BaseModel):
    home: float
    draw: float
    away: float

class MatchResponse(BaseModel):
    id: str
    competition: str
    kickoffDate: date
    homeTeam: str
    awayTeam: str
    odds: Odds

