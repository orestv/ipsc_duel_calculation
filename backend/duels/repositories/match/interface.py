import uuid

from duels.api_models import MatchInProgress, DuelOutcome, MatchOutcomes


class MatchRepository:
    async def add_match(self, match: MatchInProgress) -> uuid.UUID:
        raise NotImplementedError

    async def get_matches(self) -> list[MatchInProgress]:
        raise NotImplementedError

    async def delete_match(self, match_id: uuid.UUID) -> None:
        raise NotImplementedError

    async def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        raise NotImplementedError

    async def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        raise NotImplementedError

    async def add_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        raise NotImplementedError

    async def get_duel_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        raise NotImplementedError


