import datetime
import itertools
import uuid

import duels.model
from duels.api_models import MatchInProgress, MatchDuel, DuelOutcome, MatchCreate, MatchParticipant, MatchOutcomes, \
    ParticipantVictories


class MatchRepository:
    matches: dict[uuid.UUID, MatchInProgress]
    outcomes: dict[uuid.UUID, MatchOutcomes]

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
                    order=idx,
                    left=self._get_participant_id(duel.left.name, duel.clazz, participants),
                    right=self._get_participant_id(duel.right.name, duel.clazz, participants),
                    clazz=duel.clazz,
                )
                for idx, duel in enumerate(rng_duels, start=1)
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
        self.outcomes[match_id] = MatchOutcomes()
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

    def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        return self.outcomes[match_id]

    def record_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        outcome.created_at = datetime.datetime.now()
        match_outcomes = self.outcomes[match_id].outcomes
        if outcome.duel_id not in match_outcomes:
            match_outcomes[outcome.duel_id] = list()
        match_outcomes[outcome.duel_id].append(outcome)

    def get_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        return self.outcomes[match_id].outcomes.get(duel_id, [])

    def get_victories(self, match_id: uuid) -> list[ParticipantVictories]:
        participants = {p.id:
            ParticipantVictories(
                participant_id=p.id,
                victories=0,
            )
            for p in self.matches[match_id].participants
        }
        match_outcomes = self.outcomes[match_id].outcomes

        for duels in self.matches[match_id].duels.values():
            for duel in duels:
                if duel.id not in match_outcomes:
                    continue

                outcomes = match_outcomes[duel.id]
                outcomes = list(sorted(outcomes, key=lambda o: o.created_at))
                last_outcome = outcomes[-1]

                if last_outcome.dq:
                    if last_outcome.dq.left:
                        participants[duel.left].dq = True
                    if last_outcome.dq.right:
                        participants[duel.right].dq = True

                if last_outcome.victory.left:
                    participants[duel.left].victories += 1
                if last_outcome.victory.right:
                    participants[duel.right].victories += 1

        result = list(participants.values())
        for p in result:
            if p.dq:
                p.victories = 0

        return result