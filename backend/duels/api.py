import logging
import traceback

import pydantic
import litestar
import litestar.exceptions
from litestar.config.cors import CORSConfig

import duels.model
import duels.comp


class ClassSetup(pydantic.BaseModel):
    participants: list[str]
    twice: bool


class RangeSetup(pydantic.BaseModel):
    classes: dict[duels.model.Class, ClassSetup]


class MatchSetup(pydantic.BaseModel):
    ranges: dict[duels.model.Range, RangeSetup]


class Participant(pydantic.BaseModel):
    name: str


class Duel(pydantic.BaseModel):
    left: Participant
    right: Participant
    clazz: duels.model.Class


class Duels(pydantic.BaseModel):
    ranges: dict[duels.model.Range, list[Duel]]


class DuelsController(litestar.Controller):
    path = "/duels"

    @litestar.post()
    def get_duels(self, data: MatchSetup) -> Duels:
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
            for rng, range_setup in data.ranges.items()
        }

        result = {
            rng: duels.comp.merge_queues(d)
            for rng, d in result.items()
        }

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


def logging_exception_handler(_: litestar.Request, exc: Exception) -> litestar.Response:
    logging.exception(exc)
    return litestar.Response(
        media_type=litestar.MediaType.JSON,
        content={"error": str(exc)},
        status_code=500,
    )


app = litestar.Litestar(
    route_handlers=[DuelsController],
    cors_config=CORSConfig(allow_origins=["http://localhost:4000"]),
    exception_handlers={Exception: logging_exception_handler},
)
