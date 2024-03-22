import itertools
import uuid

import duels.model
from duels.api_models import Duels, MatchInProgress, MatchDuel, DuelOutcome, MatchCreate, MatchParticipant


class MatchRepository:
    matches: dict[uuid.UUID, MatchInProgress]
    outcomes: dict[uuid.UUID, DuelOutcome]

    def __init__(self):
        self.matches = {}
        self.outcomes = {}

    def create_match(self, match: MatchCreate) -> uuid.UUID:
        all_duels = list(itertools.chain(
            *[duel for duel in match.duels.ranges.values()]
        ))
        all_participants = list(set(itertools.chain(
            [(d.left.name, d.clazz) for d in all_duels],
            [(d.right.name, d.clazz) for d in all_duels],
        )))
        participants = [
            MatchParticipant(
                id=uuid.uuid4(),
                name=name,
                clazz=clazz,
            )
            for name, clazz in all_participants
        ]
        participants.sort()

        match_duels = {
            rng: [
                MatchDuel(
                    id=uuid.uuid4(),
                    left=self._get_participant_id(duel.left.name, duel.clazz, participants),
                    right=self._get_participant_id(duel.right.name, duel.clazz, participants),
                    clazz=duel.clazz,
                )
                for duel in rng_duels
            ]
            for rng, rng_duels in match.duels.ranges.items()
        }

        participants_by_range = {
            rng: []
            for rng in match.duels.ranges
        }
        for p in participants:
            for rng, duels in match.duels.ranges.items():
                for d in duels:
                    if d.clazz == p.clazz and p.name in (d.left.name, d.right.name):
                        participants_by_range[rng].append(p.id)
                        break

        match = MatchInProgress(
            id=uuid.uuid4(),
            name=match.name,
            participants=participants,
            participants_by_range=participants_by_range,
            duels=match_duels,
        )
        match_id = uuid.uuid4()
        self.matches[match_id] = match
        return match_id

    def _get_participant_id(self, name: str, clazz: duels.model.Class, participants: list[MatchParticipant]) -> uuid.UUID:
        for participant in participants:
            if participant.name == name and participant.clazz == clazz:
                return participant.id
        raise KeyError(f"participant {name} ({clazz}) not found")

    def get_all_matches(self) -> list[MatchInProgress]:
        return [self.matches.values()]

    def delete_match(self, match_id: uuid.UUID) -> None:
        del self.matches[match_id]

    def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        return self.matches[match_id]