import functools
import os

import duels.services
import duels.repositories


async def provide_match_repository() -> duels.repositories.MatchRepository:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    match_repository = duels.repositories.MongoMatchRepository(mongo_url)
    return match_repository


async def provide_results_repository() -> duels.repositories.ResultsRepository:
    results_path = os.getenv("RESULTS_PATH")
    if not results_path:
        return duels.repositories.results.NoopResultRepository()
    return duels.repositories.LocalResultsRepository(results_path)


async def provide_match_service(match_repository: duels.repositories.MatchRepository, results_repository: duels.repositories.results.ResultsRepository) -> duels.services.MatchService:
    return duels.services.MatchService(match_repository, results_repository)
