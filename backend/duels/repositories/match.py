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


class InMemoryMatchRepository:
    matches: dict[uuid.UUID, MatchInProgress]
    outcomes: dict[uuid.UUID, MatchOutcomes]

    def __init__(self):
        self.matches = {}
        self.outcomes = {}

    async def add_match(self, match: MatchInProgress) -> uuid.UUID:
        match.id = uuid.uuid4()
        self.matches[match.id] = match
        self.outcomes[match.id] = MatchOutcomes()
        return match.id

    async def get_matches(self) -> list[MatchInProgress]:
        return list(self.matches.values())

    async def delete_match(self, match_id: uuid.UUID) -> None:
        del self.matches[match_id]
        del self.outcomes[match_id]

    async def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        return self.matches[match_id]

    async def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        return self.outcomes[match_id]

    async def add_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        match_outcomes = self.outcomes[match_id].outcomes
        if outcome.duel_id not in match_outcomes:
            match_outcomes[outcome.duel_id] = list()
        match_outcomes[outcome.duel_id].append(outcome)

    async def get_duel_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        return self.outcomes[match_id].outcomes.get(duel_id, [])


