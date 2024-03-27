import datetime
import logging
import pathlib
import uuid
import urllib.parse
import aiofiles
import aiohttp
import aiopath

import pytz
from google.cloud import storage
from gcloud.aio.storage import Storage

from duels.repositories.results import ResultsRepository


class GCloudRepository(ResultsRepository):
    tz = pytz.timezone("Europe/Kyiv")

    def __init__(self, credentials_path: str, bucket_name: str):
        self.log = logging.getLogger(self.__class__.__name__)
        self.credentials_path = credentials_path
        self.bucket_name = bucket_name

    async def store(self, match_id: uuid.UUID, match_name: str, source_path: pathlib.Path):
        result_dir = f"{match_id}-{match_name}".replace('/', '_')
        result_filename = f"{datetime.datetime.now(self.tz)}.xlsx".replace('/', '_')
        destination_path = aiopath.AsyncPath(result_dir, result_filename)
        async with aiohttp.ClientSession() as session:
            client = Storage(session=session)
            async with aiofiles.open(source_path, "r") as f:
                self.log.info("Upload started")
                await client.upload_from_filename(
                    self.bucket_name,
                    str(destination_path),
                    str(source_path),
                )
                self.log.info("Upload successful")
