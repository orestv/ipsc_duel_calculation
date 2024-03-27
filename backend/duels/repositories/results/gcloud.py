import datetime
import pathlib
import uuid
import urllib.parse

import pytz
from google.cloud import storage

from duels.repositories.results import ResultsRepository


class GCloudRepository(ResultsRepository):
    tz = pytz.timezone("Europe/Kyiv")

    def __init__(self, credentials_path: str, bucket_name: str):
        self.credentials_path = credentials_path
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    async def store(self, match_id: uuid.UUID, match_name: str, source_path: pathlib.Path):
        result_dir = urllib.parse.quote_plus(f"{match_id}-{match_name}")
        result_filename = urllib.parse.quote_plus(f"{datetime.datetime.now(self.tz)}.xlsx")
        blob = self.bucket.blob(f"{result_dir}/{result_filename}")
        blob.upload_from_filename(str(source_path))
        import logging; logging.info("Upload successful")

