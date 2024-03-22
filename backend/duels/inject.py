import functools

from duels.repositories import MatchRepository

match_repository = MatchRepository()


async def provide_match_repository() -> MatchRepository:
    return match_repository
