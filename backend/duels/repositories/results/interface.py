import uuid


class ResultsRepository:
    async def store(self, match_id: uuid.UUID, match_name: str, path: str):
        raise NotImplementedError