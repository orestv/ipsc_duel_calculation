import uuid

from duels.repositories.results import ResultsRepository


class GCloudRepository(ResultsRepository):
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path

    async def store(self, match_id: uuid.UUID, match_name: str, path: str):
        raise NotImplementedError

