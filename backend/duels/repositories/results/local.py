import datetime
import os
import uuid
import pathlib
import aiopath
import pytz

from duels.repositories.results import ResultsRepository


class LocalResultsRepository(ResultsRepository):

    tz = pytz.timezone("Europe/Kyiv")

    def __init__(self, path: str) -> None:
        self.workdir = os.path.abspath(path)
        pathlib.Path(self.workdir).mkdir(parents=True, exist_ok=True)

    async def store(self, match_id: uuid.UUID, match_name: str, path: str):
        match_directory = await self._ensure_directory(match_id, match_name)
        result_filename = f"{datetime.datetime.now(self.tz)}.txt"
        await aiopath.AsyncPath(match_directory, result_filename).touch(exist_ok=True)

    async def _ensure_directory(self, match_id: uuid.UUID, match_name: str) -> aiopath.AsyncPath:
        dir_name = f"{match_id}_{match_name}"
        path = aiopath.AsyncPath(self.workdir, dir_name)
        await path.mkdir(parents=True, exist_ok=True)
        return path

    def _path(self, match_id: uuid.UUID, match_name: str):
        return os.path.join(
            self.workdir,
            f"{match_id}_{match_name}/"
        )