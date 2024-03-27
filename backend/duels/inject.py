import functools
import os
import typing

import duels.services
import duels.repositories


async def provide_match_repository() -> duels.repositories.MatchRepository:
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    match_repository = duels.repositories.MongoMatchRepository(mongo_url)
    return match_repository


def result_repository_factory(
        results_path: typing.Optional[str] = None,
        gcloud_credentials_path: typing.Optional[str] = None,
        gcloud_bucket_name: typing.Optional[str] = None,
) -> duels.repositories.ResultsRepository:
    if gcloud_credentials_path and gcloud_bucket_name:
        return duels.repositories.GCloudRepository(gcloud_credentials_path, gcloud_bucket_name)
    if results_path:
        return duels.repositories.LocalResultsRepository(results_path)
    return duels.repositories.NoopResultRepository()


async def provide_results_repository() -> duels.repositories.ResultsRepository:
    results_path = os.getenv("RESULTS_PATH")
    gcloud_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    gcloud_bucket_name = os.getenv("GCLOUD_BUCKET_NAME")
    return result_repository_factory(results_path, gcloud_credentials_path, gcloud_bucket_name)


async def provide_match_service(match_repository: duels.repositories.MatchRepository, results_repository: duels.repositories.results.ResultsRepository) -> duels.services.MatchService:
    return duels.services.MatchService(match_repository, results_repository)
