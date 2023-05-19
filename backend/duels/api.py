import logging
import tempfile

import litestar
import litestar.exceptions
from litestar.config.cors import CORSConfig
from litestar.response_containers import File

import duels
import duels.model
import duels.comp
import duels.comp_excel
from . import comp_excel
from duels.api_models import MatchSetup, Participant, Duel, Duels


class DuelsController(litestar.Controller):
    path = "/duels"

    @litestar.post(sync_to_thread=True)
    def get_duels(self, data: MatchSetup) -> Duels:
        result = self._generate_duels(data)

        result = Duels(ranges={
            rng: [
                Duel(
                    left=Participant(name=duel.left.name),
                    right=Participant(name=duel.right.name),
                    clazz=duel.clazz,
                )
                for duel in range_duels
            ]
            for rng, range_duels in result.items()
        })
        return result

    @litestar.post("/excel", sync_to_thread=True)
    def get_duels_excel(self, data: MatchSetup) -> File:
        range_duels = self._generate_duels(data)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as f:
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
                    clazz_setup.twice,
                )
                for clazz, clazz_setup in range_setup.classes.items()
            ]
            for rng, range_setup in match_setup.ranges.items()
        }
        result = {
            rng: duels.comp.merge_queues(d)
            for rng, d in result.items()
        }
        return result


def logging_exception_handler(_: litestar.Request, exc: Exception) -> litestar.Response:
    logging.exception(exc)
    return litestar.Response(
        media_type=litestar.MediaType.JSON,
        content={"error": str(exc)},
        status_code=500,
    )


app = litestar.Litestar(
    route_handlers=[DuelsController],
    # cors_config=CORSConfig(allow_origins=["http://localhost:4000"]),
    exception_handlers={Exception: logging_exception_handler},
)
