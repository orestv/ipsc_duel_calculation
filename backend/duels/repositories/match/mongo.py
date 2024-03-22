import uuid

from duels.api_models import MatchInProgress, MatchOutcomes, DuelOutcome
from duels.repositories.match.interface import MatchRepository


class MongoMatchRepository(MatchRepository):

    async def add_match(self, match: MatchInProgress) -> uuid.UUID:
        pass

    async def get_matches(self) -> list[MatchInProgress]:
        pass

    async def delete_match(self, match_id: uuid.UUID) -> None:
        pass

    async def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        pass

    async def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        pass

    async def add_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        pass

    async def get_duel_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        pass
