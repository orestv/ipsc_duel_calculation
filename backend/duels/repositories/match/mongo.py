import uuid

import motor.motor_asyncio

from duels.api_models import MatchInProgress, MatchOutcomes, DuelOutcome
from duels.repositories.match.interface import MatchRepository


class MongoMatchRepository(MatchRepository):

    def __init__(self, mongo_url: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            mongo_url,
            uuidRepresentation='standard',
        )
        self.db = self.client["matches"]
        self.matches = self.db["matches"]
        self.outcomes = self.db["outcomes"]

    async def add_match(self, match: MatchInProgress) -> uuid.UUID:
        match.id = uuid.uuid4()
        doc = match.dict()
        await self.matches.insert_one(doc)
        return match.id

    async def get_matches(self) -> list[MatchInProgress]:
        return await self.matches.find()

    async def delete_match(self, match_id: uuid.UUID) -> None:
        return await self.matches.delete_one({"id": match_id})

    async def get_match(self, match_id: uuid.UUID) -> MatchInProgress:
        match = await self.matches.find_one({"id": match_id})
        if not match:
            raise KeyError
        return MatchInProgress.parse_obj(match)

    async def add_outcome(self, match_id: uuid.UUID, outcome: DuelOutcome):
        doc = outcome.dict()
        doc["match_id"] = match_id
        await self.outcomes.insert_one(doc)

    async def get_match_outcomes(self, match_id: uuid.UUID) -> MatchOutcomes:
        docs = self.outcomes.find({"match_id": match_id})
        duel_outcomes = [DuelOutcome.parse_obj(doc) async for doc in docs]
        return MatchOutcomes(outcomes=duel_outcomes)

    async def get_duel_outcomes(self, match_id: uuid.UUID, duel_id: uuid.UUID) -> list[DuelOutcome]:
        docs = self.outcomes.find({"duel_id": duel_id})
        try:
            return [DuelOutcome.parse_obj(doc) async for doc in docs]
        except Exception as e:
            import logging; logging.exception(e)
