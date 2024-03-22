import datetime
import itertools
import typing
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

    def add_match(self, match: MatchInProgress) -> uuid.UUID:
        match.id = uuid.uuid4()
        self.matches[match.id] = match
        self.outcomes[match.id] = MatchOutcomes()
        return match.id

    def get_matches(self) -> list[MatchInProgress]:
        return list(self.matches.values())

    def delete_match(self, match_id: uuid.UUID) -> None:
        del self.matches[match_id]
        del self.outcomes[match_id]

    def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        return self.matches[match_id]

    def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        return self.outcomes[match_id]

    def add_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        match_outcomes = self.outcomes[match_id].outcomes
        if outcome.duel_id not in match_outcomes:
            match_outcomes[outcome.duel_id] = list()
        match_outcomes[outcome.duel_id].append(outcome)

    def get_duel_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        return self.outcomes[match_id].outcomes.get(duel_id, [])


class MatchService:
    repository: MatchRepository

    def __init__(self, repository: MatchRepository):
        self.repository = repository

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
            name=match.name,
            participants=participants,
            participants_by_range=participants_by_range,
            duels=match_duels,
        )
        match_id = self.repository.add_match(match)
        return match_id

    def _get_participant_id(self, name: str, clazz: duels.model.Class,
                            participants: list[MatchParticipant]) -> uuid.UUID:
        for participant in participants:
            if participant.name == name and participant.clazz == clazz:
                return participant.id
        raise KeyError(f"participant {name} ({clazz}) not found")

    def get_all_matches(self) -> list[MatchInProgress]:
        return self.repository.get_matches()

    def delete_match(self, match_id: uuid.UUID) -> None:
        self.repository.delete_match(match_id)

    def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        return self.repository.get_match(match_id)

    def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        return self.repository.get_match_outcomes(match_id)

    def record_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        outcome.created_at = datetime.datetime.now()
        self.repository.add_outcome(match_id, outcome)

    def get_duel_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        return self.repository.get_duel_outcomes(match_id, duel_id)

    def get_victories(self, match_id: uuid) -> list[ParticipantVictories]:
        match = self.repository.get_match(match_id)
        participants = {
            p.id: ParticipantVictories(
                participant_id=p.id,
                victories=0,
            )
            for p in match.participants
        }

        for duels in match.duels.values():
            for duel in duels:

                outcome = self._get_duel_outcome(duel, match_id)
                if not outcome:
                    continue

                if outcome.dq:
                    if outcome.dq.left:
                        participants[duel.left].dq = True
                    if outcome.dq.right:
                        participants[duel.right].dq = True

                if outcome.victory.left:
                    participants[duel.left].victories += 1
                if outcome.victory.right:
                    participants[duel.right].victories += 1

        result = list(participants.values())
        for p in result:
            if p.dq:
                p.victories = 0

        return result

    def _get_duel_outcome(self, duel, match_id) -> typing.Optional[DuelOutcome]:
        duel_outcomes = self.repository.get_duel_outcomes(match_id, duel.id)
        if not duel_outcomes:
            return None
        duel_outcomes = list(sorted(duel_outcomes, key=lambda o: o.created_at))
        last_outcome = duel_outcomes[-1]
        return last_outcome
