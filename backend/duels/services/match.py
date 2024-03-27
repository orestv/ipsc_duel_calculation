import datetime
import itertools
import typing
import uuid

import litestar.exceptions

import duels.model
from duels.api_models import MatchCreate, MatchParticipant, MatchDuel, MatchInProgress, MatchOutcomes, DuelOutcome, \
    ParticipantVictories, OutcomeDQ, OutcomeVictory
from duels.repositories import MatchRepository
from duels.repositories.results import ResultsRepository


class MatchService:
    match_repo: MatchRepository
    results_repo: ResultsRepository

    def __init__(self,
                 match_repository: MatchRepository,
                 results_repository: ResultsRepository,
             ):
        self.match_repo = match_repository
        self.results_repo = results_repository

    async def create_match(self, match: MatchCreate) -> uuid.UUID:
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
            created_at=datetime.datetime.now(),
        )
        match_id = await self.match_repo.add_match(match)
        return match_id

    def _get_participant_id(self, name: str, clazz: duels.model.Class,
                            participants: list[MatchParticipant]) -> uuid.UUID:
        for participant in participants:
            if participant.name == name and participant.clazz == clazz:
                return participant.id
        raise KeyError(f"participant {name} ({clazz}) not found")

    async def get_all_matches(self) -> list[MatchInProgress]:
        return await self.match_repo.get_matches()

    async def delete_match(self, match_id: uuid.UUID) -> None:
        await self.match_repo.delete_match(match_id)

    async def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        try:
            return await self.match_repo.get_match(match_id)
        except KeyError:
            raise litestar.exceptions.NotFoundException()

    async def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        return await self.match_repo.get_match_outcomes(match_id)

    async def record_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        outcome.created_at = datetime.datetime.now()
        await self.match_repo.add_outcome(match_id, outcome)
        if outcome.reshoot:
            await self._record_reshoot(match_id, outcome)
        elif outcome.dq:
            await self._record_dq(match_id, outcome)

    async def backup_match(self, match_id: uuid.UUID):
        match = await self.match_repo.get_match(match_id)
        await self.results_repo.store(
            match.id,
            match.name,
            "",
        )

    async def _record_reshoot(self, match_id, outcome):
        match = await self.match_repo.get_match(match_id)
        for rng, duels in match.duels.items():
            found_duels = [d for d in duels if d.id == outcome.duel_id]
            if not found_duels:
                continue
            found_duel = found_duels[0]
            reshoot_duel = found_duel.copy()
            reshoot_duel.id = uuid.uuid4()
            reshoot_duel.order = len(duels) + 1
            match.duels[rng].append(reshoot_duel)
        await self.match_repo.update_match(match)

    async def _record_dq(self, match_id: uuid.UUID, outcome: DuelOutcome):
        match = await self.match_repo.get_match(match_id)
        dq_participant_ids = await self._get_dq_participant_ids(match, outcome)
        await self._disqualify_participant(match, dq_participant_ids, outcome.duel_id)

    async def _get_dq_participant_ids(self, match: MatchInProgress, outcome: DuelOutcome) -> list[uuid.UUID]:
        all_duels = itertools.chain(*match.duels.values())
        dq_duel: MatchDuel = [d for d in all_duels if d.id == outcome.duel_id][0]
        participant_ids = []
        if outcome.dq.left:
            participant_ids.append(dq_duel.left)
        if outcome.dq.right:
            participant_ids.append(dq_duel.right)
        return participant_ids

    async def _disqualify_participant(self, match: MatchInProgress, participant_ids: list[uuid.UUID], dq_duel_id: uuid.UUID):
        all_duels = itertools.chain(*match.duels.values())
        participant_duels = [
            (d, await self._get_duel_outcome(d, match.id))
            for d in all_duels
            if any (p for p in participant_ids if p in (d.left, d.right))
        ]
        participant_duels = [
            (d, outcome)
            for d, outcome in participant_duels if not outcome or outcome.dummy
        ]
        for duel, old_outcome in participant_duels:
            # make sure that previous DQs are not overwritten
            old_dq = old_outcome.dq if old_outcome else OutcomeDQ(left=False, right=False)
            dq_left = old_dq.left or duel.left in participant_ids
            dq_right = old_dq.right or duel.right in participant_ids
            new_outcome = DuelOutcome(
                duel_id=duel.id,
                dummy=True,
                dq=OutcomeDQ(
                    left=dq_left,
                    right=dq_right,
                ),
                victory=OutcomeVictory(
                    left=not dq_left,
                    right=not dq_right,
                ),
                created_at=datetime.datetime.now(),
            )
            await self.match_repo.add_outcome(match.id, new_outcome)

    async def get_duel_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        return await self.match_repo.get_duel_outcomes(match_id, duel_id)

    async def get_victories(self, match_id: uuid) -> list[ParticipantVictories]:
        match = await self.match_repo.get_match(match_id)
        participants = {
            p.id: ParticipantVictories(
                participant_id=p.id,
                victories=0,
            )
            for p in match.participants
        }

        for duels in match.duels.values():
            for duel in duels:

                outcome = await self._get_duel_outcome(duel, match_id)
                if not outcome:
                    continue

                if outcome.dq:
                    if outcome.dq.left:
                        participants[duel.left].dq = True
                    if outcome.dq.right:
                        participants[duel.right].dq = True

                if outcome.victory:
                    if outcome.victory.left:
                        participants[duel.left].victories += 1
                    if outcome.victory.right:
                        participants[duel.right].victories += 1

        result = list(participants.values())
        for p in result:
            if p.dq:
                p.victories = 0

        return result

    async def _get_duel_outcome(self, duel, match_id) -> typing.Optional[DuelOutcome]:
        duel_outcomes = await self.match_repo.get_duel_outcomes(match_id, duel.id)
        if not duel_outcomes:
            return None
        duel_outcomes = list(sorted(duel_outcomes, key=lambda o: o.created_at))
        last_outcome = duel_outcomes[-1]
        return last_outcome
