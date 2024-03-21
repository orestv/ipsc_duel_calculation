import uuid

from duels.api_models import Duels, MatchDuels, MatchDuel, DuelOutcome


class MatchRepository:
    matches: dict[uuid.UUID, MatchDuels]
    outcomes: dict[uuid.UUID, DuelOutcome]

    def __init__(self):
        self.matches = {}
        self.outcomes = {}

    def create_match(self, duels: Duels) -> uuid.UUID:
        match_duels = {
            rng: [
                MatchDuel(
                    id=uuid.uuid4(),
                    left=duel.left,
                    right=duel.right,
                    clazz=duel.clazz,
                )
                for duel in rng_duels
            ]
            for rng, rng_duels in duels.ranges.items()
        }
        match = MatchDuels(ranges=match_duels)
        match_id = uuid.uuid4()
        self.matches[match_id] = match
        return match_id

    def get_match(self, match_id: uuid.UUID) -> MatchDuels:
        return self.matches[match_id]