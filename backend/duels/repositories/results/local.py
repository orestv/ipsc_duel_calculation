import os
import uuid
import pathlib

from duels.repositories.results import ResultsRepository


class LocalResultsRepository(ResultsRepository):
    def __init__(self, path: str) -> None:
        self.workdir = os.path.abspath(path)
        pathlib.Path(self.workdir).mkdir(parents=True, exist_ok=True)

    def store(self, match_id: uuid.UUID, match_name: str, path: str):
        pass

    def _path(self, match_id: uuid.UUID, match_name: str):
        return os.path.join(
            self.workdir,
            f"{match_id}_{match_name}/"
        )