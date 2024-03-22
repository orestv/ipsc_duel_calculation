import functools
import os

from duels.services import MatchService
from duels.repositories import InMemoryMatchRepository

mongo_url = os.getenv("MONGO_URL")
match_repository = InMemoryMatchRepository()


async def provide_match_repository() -> InMemoryMatchRepository:
    return match_repository


async def provide_match_service(match_repository: InMemoryMatchRepository) -> MatchService:
    return MatchService(match_repository)
