from pydantic import BaseModel
from datetime import date

class Odds(BaseModel):
    home: float
    draw: float
    away: float

class MatchResponse(BaseModel):
    id: str
    competition: str
    kickoffDate: date
    awayTeam: str
    odds: Odds

