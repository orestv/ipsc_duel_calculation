import functools
import os

from duels.services import MatchService
from duels.repositories import InMemoryMatchRepository, MongoMatchRepository, MatchRepository

async def provide_match_repository() -> MatchRepository:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    match_repository = MongoMatchRepository(mongo_url)
    return match_repository


async def provide_match_service(match_repository: MatchRepository) -> MatchService:
    return MatchService(match_repository)
