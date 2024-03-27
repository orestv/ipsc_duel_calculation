import pathlib
import uuid


class ResultsRepository:
    async def store(self, match_id: uuid.UUID, match_name: str, source_path: pathlib.Path):
        raise NotImplementedError