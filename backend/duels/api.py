import logging
import tempfile
import uuid

import litestar
import litestar.exceptions
from litestar.exceptions import NotFoundException
from litestar.response import File
from litestar.di import Provide

import duels
import duels.comp
import duels.comp_excel
import duels.model
from duels.api_models import MatchSetup, Participant, Duel, Duels, MatchDuels
from . import comp_excel
from .inject import provide_match_repository
from .repositories import MatchRepository


class DuelsController(litestar.Controller):
    path = "/duels"

    @litestar.post(sync_to_thread=True)
    def get_duels(self, data: MatchSetup) -> Duels:
        result = self._generate_duels(data)

        result = Duels(
            ranges={
                rng: [
                    Duel(
                        left=Participant(name=duel.left.name),
                        right=Participant(name=duel.right.name),
                        clazz=duel.clazz,
                    )
                    for duel in range_duels
                ]
                for rng, range_duels in result.items()
            }
        )
        return result

    @litestar.post("/excel", sync_to_thread=True)
    def get_duels_excel(self, data: MatchSetup) -> File:
        range_duels = self._generate_duels(data)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as f:
            pass

        path = f.name

        comp_excel.deliver_excel(range_duels, path)
        return File(path=path, filename="pairs.xlsx")

    def _generate_duels(self, match_setup: MatchSetup):
        result = {
            rng: [
                duels.comp.generate_duels(
                    [
                        duels.model.Participant(name, clazz)
                        for name in clazz_setup.participants
                    ],
                    clazz_setup.times,
                )
                for clazz, clazz_setup in range_setup.classes.items()
            ]
            for rng, range_setup in match_setup.ranges.items()
        }
        result = {rng: duels.comp.merge_queues(d) for rng, d in result.items()}
        return result


class MatchController(litestar.Controller):
    path = "/matches"

    @litestar.post(
        dependencies={
            "match_repository": Provide(provide_match_repository)
        }
    )
    async def create_match(self, data: Duels, match_repository: MatchRepository) -> uuid.UUID:
        return match_repository.create_match(data)

    @litestar.get("/{match_id:uuid}",
                  dependencies={"match_repository": Provide(provide_match_repository)}
                  )
    async def get_match(self, match_id: uuid.UUID, match_repository: MatchRepository) -> MatchDuels:
        try:
            result = match_repository.get_match(match_id)
            return result
        except KeyError:
            raise NotFoundException()


def logging_exception_handler(_: litestar.Request, exc: Exception) -> litestar.Response:
    logging.exception(exc)
    return litestar.Response(
        media_type=litestar.MediaType.JSON,
        content={"error": str(exc)},
        status_code=500,
    )


app = litestar.Litestar(
    route_handlers=[DuelsController, MatchController],
    # cors_config=CORSConfig(allow_origins=["http://localhost:4000"]),
    # exception_handlers={Exception: logging_exception_handler},
)
