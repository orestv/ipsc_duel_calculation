import uuid

from duels.repositories.results import ResultsRepository

import logging


class NoopResultRepository(ResultsRepository):
    log = logging.getLogger("NoopResultRepository")

    async def store(self, match_id: uuid.UUID, match_name: str, path: str):
        logging.info("Pretending to back up match %s", match_id)