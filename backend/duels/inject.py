import functools

from duels.repositories import MatchService
from duels.repositories.matches import MatchRepository

match_repository = MatchRepository()


async def provide_match_repository() -> MatchRepository:
    return match_repository


async def provide_match_service(match_repository: MatchRepository) -> MatchService:
    return MatchService(match_repository)
