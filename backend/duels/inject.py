import functools

from duels.repositories import MatchRepository

match_repository = MatchRepository()

async def provide_match_repository() -> MatchRepository:
    print("Creating match repository")
    return match_repository
